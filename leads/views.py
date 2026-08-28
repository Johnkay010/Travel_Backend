import uuid
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lead, Payment
from .serializers import (
    LeadSerializer,
    PaymentInitSerializer,
    PaymentSerializer,
    PaymentVerifySerializer,
)

PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/{reference}"


@method_decorator(csrf_exempt, name="dispatch")
class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [AllowAny]


class PaymentInitializeView(APIView):
    """POST /api/payments/initialize/

    Called right before the frontend opens the Paystack popup. Creates a
    PENDING Payment row with a backend-generated reference and the
    backend's own fee amount (settings.CONSULTATION_FEE_KOBO) — the
    frontend uses exactly these values to open Paystack, it never invents
    its own amount or reference.
    """

    def post(self, request):
        serializer = PaymentInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reference = f"HAE-{uuid.uuid4().hex[:14]}"
        payment = Payment.objects.create(
            full_name=serializer.validated_data["full_name"],
            email=serializer.validated_data["email"],
            phone=serializer.validated_data["phone"],
            reference=reference,
            amount_kobo=settings.CONSULTATION_FEE_KOBO,
            status=Payment.Status.PENDING,
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentVerifyView(APIView):
    """POST /api/payments/verify/

    Called after the Paystack popup's callback fires with a reference.
    Never trusts the browser's report of success — independently asks
    Paystack's servers to confirm the transaction, and cross-checks the
    verified amount against what we expected before marking it paid.
    """

    def post(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference = serializer.validated_data["reference"]

        try:
            payment = Payment.objects.get(reference=reference)
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Unknown payment reference."}, status=status.HTTP_404_NOT_FOUND
            )

        # Idempotent: if we already confirmed this one, don't re-hit Paystack.
        if payment.status == Payment.Status.SUCCESS:
            return Response(PaymentSerializer(payment).data)

        if not settings.PAYSTACK_SECRET_KEY:
            return Response(
                {"detail": "Payment verification is not configured on the server yet."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            paystack_response = requests.get(
                PAYSTACK_VERIFY_URL.format(reference=reference),
                headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
                timeout=15,
            )
            payload = paystack_response.json()
        except (requests.RequestException, ValueError):
            return Response(
                {"detail": "Could not reach Paystack to verify this payment. Try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = payload.get("data") or {}
        paid_successfully = (
            payload.get("status") is True
            and data.get("status") == "success"
            and data.get("currency") == "NGN"
            and data.get("amount") == payment.amount_kobo
        )

        payment.paystack_payload = payload

        if not paid_successfully:
            payment.status = Payment.Status.FAILED
            payment.save()
            reason = data.get("gateway_response") or "Payment could not be verified."
            return Response({"detail": reason}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = Payment.Status.SUCCESS
        payment.verified_at = timezone.now()

        lead = Lead.objects.create(
            full_name=payment.full_name,
            email=payment.email,
            phone=payment.phone,
            source=Lead.Source.BOOK_CONSULTATION,
            agreed_terms=True,
            agreed_privacy=True,
            consent_contact=True,
        )
        payment.lead = lead
        payment.save()

        return Response(PaymentSerializer(payment).data)

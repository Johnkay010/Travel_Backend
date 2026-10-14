from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Lead, Subscriber
from .serializers import LeadSerializer, SubscriberSerializer


def csrf_test(request):
    return JsonResponse(
        {"status": "ok", "message": "Render is running this version of the backend"}
    )


@method_decorator(csrf_exempt, name="dispatch")
class LeadCreateView(generics.CreateAPIView):
    """POST /api/leads/ — used by the Get Started form.

    csrf_exempt + AllowAny + no authentication_classes: this endpoint is
    public (no login), and Django's session-based CSRF check doesn't apply
    to it — kept exactly as configured to fix the cross-origin POST issue
    on Render.
    """

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


@method_decorator(csrf_exempt, name="dispatch")
class SubscriberCreateView(generics.CreateAPIView):
    """POST /api/subscribe/ — used by both the entry modal and the footer
    subscription form. Same public-endpoint CSRF setup as LeadCreateView.

    Duplicate emails are normally caught by SubscriberSerializer's
    UniqueValidator before anything touches the database, returning a
    clean 400 with {"email": ["This email is already subscribed."]}. The
    try/except below is a second line of defense against a race condition
    (two near-simultaneous submissions for the same new email both passing
    validation before either INSERT completes) — without it, that edge
    case would surface as a raw 500 IntegrityError instead of the same
    friendly 400 response.
    """

    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return Response(
                {"email": ["This email is already subscribed."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

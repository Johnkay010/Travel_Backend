from django.urls import path

from .views import LeadCreateView, PaymentInitializeView, PaymentVerifyView,csrf_test
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path("test/", csrf_test),
    path(
    "leads/",
    csrf_exempt(LeadCreateView.as_view()),
    name="lead-create",
),
    path("payments/initialize/", PaymentInitializeView.as_view(), name="payment-initialize"),
    path("payments/verify/", PaymentVerifyView.as_view(), name="payment-verify"),
]

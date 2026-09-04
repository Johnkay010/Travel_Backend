from django.urls import path

from .views import LeadCreateView, SubscriberCreateView, csrf_test

urlpatterns = [
    path("test/", csrf_test),
    path("leads/", LeadCreateView.as_view(), name="lead-create"),
    path("subscribe/", SubscriberCreateView.as_view(), name="subscriber-create"),
]

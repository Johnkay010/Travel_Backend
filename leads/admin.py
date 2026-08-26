from django.contrib import admin

from .models import Lead, Payment


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone",
        "target_destination",
        "service_needed",
        "source",
        "created_at",
    )
    list_filter = ("source", "target_destination", "service_needed", "study_timeline")
    search_fields = ("full_name", "email", "phone")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "reference",
        "amount_kobo",
        "status",
        "created_at",
        "verified_at",
    )
    list_filter = ("status",)
    search_fields = ("full_name", "email", "reference")
    readonly_fields = ("paystack_payload",)

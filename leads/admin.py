from django.contrib import admin

from .models import Lead


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

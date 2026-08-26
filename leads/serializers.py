from rest_framework import serializers

from .models import Lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "target_destination",
            "highest_qualification",
            "proof_of_funds",
            "has_funds_evidence",
            "study_timeline",
            "service_needed",
            "agreed_terms",
            "agreed_privacy",
            "consent_contact",
            "source",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # The copy doc marks these three checkboxes "Required to Submit" on
        # the Get Started page. Book Consultation submissions reuse this
        # serializer with source=book_consultation and a lighter field set,
        # so only enforce the checkboxes for the full intake form.
        if attrs.get("source", Lead.Source.GET_STARTED) == Lead.Source.GET_STARTED:
            missing = [
                field
                for field in ("agreed_terms", "agreed_privacy", "consent_contact")
                if not attrs.get(field)
            ]
            if missing:
                raise serializers.ValidationError(
                    {field: "This must be accepted to submit." for field in missing}
                )
        return attrs

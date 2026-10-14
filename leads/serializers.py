from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Lead, Subscriber


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
            "consent_contact",
            "source",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # The copy doc marks these three checkboxes "Required to Submit" on
        # the Get Started page.
        missing = [
            field
            for field in ("agreed_terms",  "consent_contact")
            if not attrs.get(field)
        ]
        if missing:
            raise serializers.ValidationError(
                {field: "This must be accepted to submit." for field in missing}
            )
        return attrs


class SubscriberSerializer(serializers.ModelSerializer):
    # Subscriber.email already has unique=True, which DRF would enforce with
    # its own default UniqueValidator message. Overriding it here gives a
    # clean, predictable 400 payload the frontend can key off directly:
    # {"email": ["This email is already subscribed."]} — no IntegrityError
    # ever reaches the database, since DRF validates before saving.
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Subscriber.objects.all(),
                message="This email is already subscribed.",
            )
        ]
    )

    class Meta:
        model = Subscriber
        fields = ["id", "name", "email", "created_at"]
        read_only_fields = ["id", "created_at"]

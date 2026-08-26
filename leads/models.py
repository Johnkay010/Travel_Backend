from django.db import models


class Lead(models.Model):
    """A prospective student who submitted the intake form.

    Field choices mirror the copy doc's "Get Started" form and the
    lightweight capture on "Book Consultation". Extend this — don't
    bolt fields onto the frontend without adding them here first.
    """

    class Destination(models.TextChoices):
        CANADA = "canada", "Canada"
        UK = "uk", "UK"
        IRELAND = "ireland", "Ireland"
        AUSTRALIA = "australia", "Australia"
        SPAIN = "spain", "Spain"
        MALTA = "malta", "Malta"
        DUBAI = "dubai", "Dubai"
        FRANCE = "france", "France"

    class Qualification(models.TextChoices):
        BSC_FIRST_2_1 = "bsc_first_2_1", "Bachelor's Degree (1st Class / 2:1)"
        BSC_2_2_THIRD = "bsc_2_2_third", "Bachelor's Degree (2:2 / 3rd Class)"
        HND = "hnd", "HND"
        MASTERS = "masters", "Master's"
        SECONDARY = "secondary", "O'Level / Secondary"

    class Budget(models.TextChoices):
        RANGE_15_25M = "15m_25m", "\u20a615M \u2013 \u20a625M"
        RANGE_25_40M = "25m_40m", "\u20a625M \u2013 \u20a640M"
        RANGE_40M_PLUS = "40m_plus", "\u20a640M+"
        NEED_GUIDANCE = "need_guidance", "Still planning / Need financial guidance"

    class Timeline(models.TextChoices):
        NEXT_INTAKE = "next_intake", "Next Available Intake"
        WITHIN_6_MONTHS = "within_6_months", "Within 6 Months"
        WITHIN_12_MONTHS = "within_12_months", "Within 12 Months"
        JUST_EXPLORING = "just_exploring", "Just Exploring"

    class ServiceNeeded(models.TextChoices):
        ADMISSIONS = "admissions", "University Admissions"
        VISA_SUPPORT = "visa_support", "Visa Application Support"
        FAMILY_RELOCATION = "family_relocation", "Family Relocation"
        UNSURE = "unsure", "Unsure / Need Consultation"

    class Source(models.TextChoices):
        GET_STARTED = "get_started", "Get Started form"
        BOOK_CONSULTATION = "book_consultation", "Book Consultation (paid)"

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField("Phone / WhatsApp number", max_length=50)

    target_destination = models.CharField(
        max_length=20, choices=Destination.choices, blank=True
    )
    highest_qualification = models.CharField(
        max_length=20, choices=Qualification.choices, blank=True
    )
    proof_of_funds = models.CharField(max_length=20, choices=Budget.choices, blank=True)
    has_funds_evidence = models.CharField(
        "Has evidence of stated funds now, or within 30 days",
        max_length=10,
        blank=True,
    )
    study_timeline = models.CharField(max_length=20, choices=Timeline.choices, blank=True)
    service_needed = models.CharField(
        max_length=20, choices=ServiceNeeded.choices, blank=True
    )

    agreed_terms = models.BooleanField(default=False)
    agreed_privacy = models.BooleanField(default=False)
    consent_contact = models.BooleanField(default=False)

    source = models.CharField(
        max_length=20, choices=Source.choices, default=Source.GET_STARTED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.email}) \u2013 {self.get_source_display()}"

    class Meta:
        ordering = ["-created_at"]


class Payment(models.Model):
    """A Paystack transaction for the paid Book Consultation session.

    Created as PENDING the moment the frontend asks us for a reference,
    then flipped to SUCCESS/FAILED only after the backend independently
    calls Paystack's Verify Transaction endpoint — never on the strength
    of what the browser reports. See leads/views.py PaymentVerifyView.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    lead = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)

    reference = models.CharField(max_length=100, unique=True)
    amount_kobo = models.PositiveIntegerField(
        help_text="Amount in kobo (\u20a61 = 100 kobo)."
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paystack_payload = models.JSONField(
        blank=True, null=True, help_text="Raw response from Paystack's verify call, for audit."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} \u2013 {self.reference} ({self.status})"

    class Meta:
        ordering = ["-created_at"]

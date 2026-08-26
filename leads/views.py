from rest_framework import generics

from .models import Lead
from .serializers import LeadSerializer


class LeadCreateView(generics.CreateAPIView):
    """POST /api/leads/ — used by both the Get Started form and the
    Book Consultation page's contact capture (distinguished by `source`).
    """

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

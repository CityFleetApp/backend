from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Benefit
from .serializers import BenefitSerializer


class BenefitViewSet(ReadOnlyModelViewSet):
    serializer_class = BenefitSerializer
    queryset = Benefit.objects.all()

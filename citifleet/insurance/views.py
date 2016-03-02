from rest_framework import viewsets

from .models import InsuranceBroker
from .serializers import InsuranceBrokerSerializer


class BrokerViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of accounting services.
    POST/PUT/DELETE - not available
    '''
    serializer_class = InsuranceBrokerSerializer
    queryset = InsuranceBroker.objects.all()

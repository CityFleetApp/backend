from rest_framework import viewsets

from .models import InsuranceBroker, Accounting
from .serializers import InsuranceBrokerSerializer, AccountingSerializer


class BrokerViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of accounting services.
    POST/PUT/DELETE - not available
    '''
    serializer_class = InsuranceBrokerSerializer
    queryset = InsuranceBroker.objects.all()


class AccountingViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of accounting services.
    POST/PUT/DELETE - not available
    '''
    serializer_class = AccountingSerializer
    queryset = Accounting.objects.all()

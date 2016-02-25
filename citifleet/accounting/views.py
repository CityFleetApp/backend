from rest_framework import viewsets

from .models import Accounting
from .serializers import AccountingSerializer


class AccountingViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of accounting services.
    POST/PUT/DELETE - not available
    '''
    serializer_class = AccountingSerializer
    queryset = Accounting.objects.all()

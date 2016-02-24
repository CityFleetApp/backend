from rest_framework import viewsets

from .models import Accounting
from .serializers import AccountingSerializer


class AccountingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccountingSerializer
    queryset = Accounting.objects.all()

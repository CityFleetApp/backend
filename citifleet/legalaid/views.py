from rest_framework import viewsets

from .models import InsuranceBroker, Accounting, DMVLawyer, TLCLawyer
from .serializers import InsuranceBrokerSerializer, AccountingSerializer, DMVLawyerSerializer, TLCLawyerSerializer


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


class DMVLawyerViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of DMV lawyers
    POST/PUT/DELETE - not available
    '''
    serializer_class = DMVLawyerSerializer
    queryset = DMVLawyer.objects.all()


class TLCLawyerViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of TLC lawyers
    POST/PUT/DELETE - not available
    '''
    serializer_class = TLCLawyerSerializer
    queryset = TLCLawyer.objects.all()

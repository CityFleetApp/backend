from rest_framework import viewsets
from rest_framework import filters

from .models import InsuranceBroker, Accounting, DMVLawyer, TLCLawyer, Location
from .serializers import (InsuranceBrokerSerializer, AccountingSerializer, DMVLawyerSerializer,
                          TLCLawyerSerializer, LocationSerializer)


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()


class LegalAidMixin(object):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('location',)


class BrokerViewSet(LegalAidMixin, viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of accounting services.
    POST/PUT/DELETE - not available
    '''
    serializer_class = InsuranceBrokerSerializer
    queryset = InsuranceBroker.objects.all()


class AccountingViewSet(LegalAidMixin, viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of accounting services.
    POST/PUT/DELETE - not available
    '''
    serializer_class = AccountingSerializer
    queryset = Accounting.objects.all()


class DMVLawyerViewSet(LegalAidMixin, viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of DMV lawyers
    POST/PUT/DELETE - not available
    '''
    serializer_class = DMVLawyerSerializer
    queryset = DMVLawyer.objects.all()


class TLCLawyerViewSet(LegalAidMixin, viewsets.ReadOnlyModelViewSet):
    '''
    GET - returns list of TLC lawyers
    POST/PUT/DELETE - not available
    '''
    serializer_class = TLCLawyerSerializer
    queryset = TLCLawyer.objects.all()

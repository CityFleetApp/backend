from rest_framework import viewsets
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework import status

from .models import Car, CarMake, CarModel, GeneralGood, JobOffer
from .serializers import (CarSerializer, CarMakeSerializer, CarModelSerializer,
                          RentCarPostingSerializer, SaleCarPostingSerializer,
                          GeneralGoodSerializer, PostingGeneralGoodsSerializer,
                          MarketplaceJobOfferSerializer, PostingJobOfferSerializer)


class PostCarRentViewSet(viewsets.ModelViewSet):
    serializer_class = RentCarPostingSerializer
    queryset = Car.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CarSerializer
        else:
            return RentCarPostingSerializer

    def get_queryset(self):
        return super(PostCarRentViewSet, self).get_queryset().filter(owner=self.request.user, rent=True)


class PostCarSaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleCarPostingSerializer
    queryset = Car.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CarSerializer
        else:
            return SaleCarPostingSerializer

    def get_queryset(self):
        return super(PostCarSaleViewSet, self).get_queryset().filter(owner=self.request.user, rent=False)


class CarRentModelViewSet(viewsets.ModelViewSet):
    serializer_class = CarSerializer
    queryset = Car.objects.filter(rent=True)


class CarSaleModelViewSet(viewsets.ModelViewSet):
    serializer_class = CarSerializer
    queryset = Car.objects.filter(rent=False)


class CarMakeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CarMakeSerializer
    queryset = CarMake.objects.all()


class CarModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CarModelSerializer
    queryset = CarModel.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('make',)


class FuelList(APIView):

    def get(self, request, *args, **kwargs):
        return Response([{'id': k, 'name': v} for k, v in Car.FUEL_TYPES])

fuel_types = FuelList.as_view()


class TypeList(APIView):

    def get(self, request, *args, **kwargs):
        return Response([{'id': k, 'name': v} for k, v in Car.TYPES])

car_types = TypeList.as_view()


class ColorList(APIView):

    def get(self, request, *args, **kwargs):
        return Response([{'id': k, 'name': v} for k, v in Car.COLORS])

colors = ColorList.as_view()


class SeatsList(APIView):

    def get(self, request, *args, **kwargs):
        return Response([{'id': k, 'name': '{} Seats'.format(k)} for k in range(4, 9)])

seats = SeatsList.as_view()


class PostingGeneralGoodsViewSet(viewsets.ModelViewSet):
    queryset = GeneralGood.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GeneralGoodSerializer
        else:
            return PostingGeneralGoodsSerializer

    def get_queryset(self):
        return super(PostingGeneralGoodsViewSet, self).get_queryset().filter(owner=self.request.user)


class MarketGeneralGoodsViewSet(viewsets.ModelViewSet):
    serializer_class = GeneralGoodSerializer
    queryset = GeneralGood.objects.all()


class PostingJobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return MarketplaceJobOfferSerializer
        else:
            return PostingJobOfferSerializer

    def get_queryset(self):
        return super(PostingJobOfferViewSet, self).get_queryset().filter(owner=self.request.user)


class MarketJobOfferViewSet(viewsets.ModelViewSet):
    serializer_class = MarketplaceJobOfferSerializer
    queryset = JobOffer.objects.filter(status__in=(JobOffer.AVAILABLE, JobOffer.COVERED))

    @detail_route(methods=['post'])
    def request_job(self, request, pk):
        offer = self.get_object()
        offer.driver_requests.add(request.user)
        return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def accept_job(self, request, pk):
        offer = self.get_object()
        # TODO: save rating
        offer.status = JobOffer.COMPLETED
        return Response(status=status.HTTP_200_OK)


class JobTypes(APIView):

    def get(self, request, *args, **kwargs):
        return Response([{'id': k, 'name': v} for k, v in JobOffer.JOB_CHOICES])

job_types = JobTypes.as_view()


class VehicleChoices(APIView):

    def get(self, request, *args, **kwargs):
        return Response([{'id': k, 'name': v} for k, v in JobOffer.VEHICLE_CHOICES])

vehicle_choices = VehicleChoices.as_view()

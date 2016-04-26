from django.views.generic import View
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from rest_framework import viewsets
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .models import Car, CarMake, CarModel, GeneralGood, JobOffer, CarPhoto, GoodPhoto
from .serializers import (CarSerializer, CarMakeSerializer, CarModelSerializer,
                          RentCarPostingSerializer, SaleCarPostingSerializer,
                          GeneralGoodSerializer, PostingGeneralGoodsSerializer,
                          MarketplaceJobOfferSerializer, PostingJobOfferSerializer,
                          CarPhotoSerializer, GoodsPhotoSerializer, CompleteJobSerializer)


class PostCarRentViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for posting cars rent
    Use different serializers for retrieving and updating car info,
    because of creating cars with relation to car photos
    '''
    serializer_class = RentCarPostingSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CarSerializer
        else:
            return RentCarPostingSerializer

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user, rent=True)


class PostCarSaleViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for posting cars for sale
    Use different serializers for retrieving and updating car info,
    because of creating cars with relation to car photos
    '''
    serializer_class = SaleCarPostingSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CarSerializer
        else:
            return SaleCarPostingSerializer

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user, rent=False)


class CarRentModelViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for retrieving cars for rent in marketplace section
    '''
    serializer_class = CarSerializer
    queryset = Car.objects.filter(rent=True)
    pagination_class = PageNumberPagination
    page_size = 20


class CarSaleModelViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for retrieving cars for sale in marketplace section
    '''
    serializer_class = CarSerializer
    queryset = Car.objects.filter(rent=False)
    pagination_class = PageNumberPagination
    page_size = 20


class CarMakeViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    ViewSet for retrieving available Car Make choices
    Used in car create/edit form
    '''
    serializer_class = CarMakeSerializer
    queryset = CarMake.objects.all()


class CarModelViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    ViewSet for retrieving available Car Model choices
    Allows filtering by Car Make type
    Used in car create/edit form
    '''
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
    pagination_class = PageNumberPagination
    page_size = 20


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
    pagination_class = PageNumberPagination
    page_size = 20

    @detail_route(methods=['post'])
    def request_job(self, request, pk):
        offer = self.get_object()
        offer.driver_requests.add(request.user)
        return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def complete_job(self, request, pk):
        serializer = CompleteJobSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)

        offer = self.get_object()
        offer.owner_rating = serializer.validated_data['rating']
        offer.paid_on_time = serializer.validated_data['paid_on_time']
        offer.status = JobOffer.COMPLETED
        offer.save()
        return Response(status=status.HTTP_200_OK)


class JobTypes(APIView):

    def get(self, request, *args, **kwargs):
        return Response([{'id': k, 'name': v} for k, v in JobOffer.JOB_CHOICES])

job_types = JobTypes.as_view()


class VehicleChoices(APIView):

    def get(self, request, *args, **kwargs):
        return Response([{'id': k, 'name': v} for k, v in JobOffer.VEHICLE_CHOICES])

vehicle_choices = VehicleChoices.as_view()


class ManagePosts(APIView):
    '''
    ViewSet with all postings created by the user ordered by creation date
    '''

    def get(self, request, *args, **kwargs):
        offers = MarketplaceJobOfferSerializer(JobOffer.objects.filter(owner=request.user),
                                               many=True).data
        for offer in offers:
            offer.update({'posting_type': 'offer'})

        goods = GeneralGoodSerializer(GeneralGood.objects.filter(owner=request.user),
                                      many=True).data
        for good in goods:
            good.update({'posting_type': 'goods'})

        cars = CarSerializer(Car.objects.filter(owner=request.user),
                             many=True).data
        for car in cars:
            car.update({'posting_type': 'car'})

        postings = sorted(offers + goods + cars, key=lambda x: x['created'])
        return Response(postings, status=status.HTTP_200_OK)

manage_posts = ManagePosts.as_view()


class CarPhotoViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for CRUD operations with photos of existing cars
    '''
    queryset = CarPhoto.objects.all()
    serializer_class = CarPhotoSerializer


class GoodsPhotoViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for CRUD operations with photos of existing goods
    '''
    queryset = GoodPhoto.objects.all()
    serializer_class = GoodsPhotoSerializer


class AwardJobView(View):

    def get(self, request, *args, **kwargs):
        job_offer = JobOffer.objects.get(id=kwargs['job_id'])
        driver = get_user_model().objects.get(id=kwargs['driver_id'])
        job_offer.award(driver)
        return HttpResponseRedirect(reverse('admin:marketplace_joboffer_change', args=[job_offer.id]))

award_job = AwardJobView.as_view()

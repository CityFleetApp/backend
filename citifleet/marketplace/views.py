from rest_framework import viewsets
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Car, CarMake, CarModel
from .serializers import CarSerializer, CarMakeSerializer, CarModelSerializer


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

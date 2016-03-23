from rest_framework import viewsets
from rest_framework import filters

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

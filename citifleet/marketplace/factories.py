from factory import DjangoModelFactory


from .models import CarModel, CarMake


class CarMakeFactory(DjangoModelFactory):

    class Meta:
        model = CarMake


class CarModelFactory(DjangoModelFactory):

    class Meta:
        model = CarModel

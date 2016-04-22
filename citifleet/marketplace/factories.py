from factory import DjangoModelFactory

from django.utils import timezone

from .models import CarModel, CarMake, JobOffer


class CarMakeFactory(DjangoModelFactory):

    class Meta:
        model = CarMake


class CarModelFactory(DjangoModelFactory):

    class Meta:
        model = CarModel


class JobOfferFactory(DjangoModelFactory):
    pickup_datetime = timezone.now()
    fare = 50
    gratuity = 5.0
    vehicle_type = JobOffer.BLACK
    job_type = JobOffer.DROP_OFF

    class Meta:
        model = JobOffer

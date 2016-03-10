import factory
from factory import DjangoModelFactory

from .models import Benefit


class BenefitFactory(DjangoModelFactory):
    image = factory.django.ImageField(color='blue')

    class Meta:
        model = Benefit

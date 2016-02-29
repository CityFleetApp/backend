from django.contrib.auth.hashers import make_password

import factory
from factory import DjangoModelFactory

from citifleet.common.test_utils import FuzzyPoint

from .models import User


class UserFactory(DjangoModelFactory):
    hack_license = factory.Faker('ean8')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    full_name = factory.Faker('name')
    username = factory.Faker('name')
    password = make_password('password')
    location = FuzzyPoint()
    bio = factory.Faker('text')
    drives = factory.Faker('word')
    avatar = factory.django.ImageField(color='blue')

    class Meta:
        model = User

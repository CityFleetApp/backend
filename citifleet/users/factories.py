from django.contrib.auth.hashers import make_password

import factory
from factory import DjangoModelFactory

from .models import User


class UserFactory(DjangoModelFactory):
    hack_license = factory.Faker('ean8')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    full_name = factory.Faker('name')
    password = make_password('password')

    class Meta:
        model = User

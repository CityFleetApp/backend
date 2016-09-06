# -*- coding: utf-8 -*-

import random
import string

from django.contrib.auth.hashers import make_password

import factory
from factory import DjangoModelFactory

from citifleet.common.test_utils import FuzzyPoint

from .models import User, Photo


class UserFactory(DjangoModelFactory):
    hack_license = factory.Faker('ean8')
    phone = factory.LazyAttribute(lambda x: ''.join([random.choice(string.digits) for n in range(11)]))
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


class PhotoFactory(DjangoModelFactory):
    file = factory.django.ImageField(color='blue')

    class Meta:
        model = Photo

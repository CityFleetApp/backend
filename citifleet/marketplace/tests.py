from tempfile import NamedTemporaryFile

from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image

from citifleet.users.factories import UserFactory

from .factories import CarMakeFactory, CarModelFactory
from .models import CarPhoto


class TestMarketPlaceViewSet(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.make = CarMakeFactory()
        self.model = CarModelFactory(make=self.make)

    def test_login_required(self):
        resp = self.client.get(reverse('marketplace:sale-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_car(self):
        self.client.force_authenticate(user=self.user)

        tmp_file1 = NamedTemporaryFile(suffix='.jpg')
        image = Image.new('RGB', (100, 100))
        image.save(tmp_file1)

        tmp_file2 = NamedTemporaryFile(suffix='.jpg')
        image = Image.new('RGB', (100, 100))
        image.save(tmp_file2)

        data = {
            'make': self.make.id, 'model': self.model.id, 'type': 1, 'color': 1, 'year': 2012,
            'fuel': 1, 'seats': 5, 'price': 5000, 'description': 'Text',
            'photos': [tmp_file1, tmp_file2]
        }

        resp = self.client.post(reverse('marketplace:postings-rent-list'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

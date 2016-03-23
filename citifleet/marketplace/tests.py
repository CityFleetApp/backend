from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory


class TestMarketPlaceViewSet(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()

    def test_login_required(self):
        resp = self.client.get(reverse('marketplace:sale-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_car(self):
        self.client.force_authenticate(user=self.user)

        resp = self.client.post(reverse('marketplace:sale-list'))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

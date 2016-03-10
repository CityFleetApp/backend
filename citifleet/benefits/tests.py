from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .factories import BenefitFactory


class TestBenefitViewSet(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()

    def test_login_required(self):
        resp = self.client.get(reverse('benefits:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_benefit_list(self):
        BenefitFactory.create_batch(10)
        self.client.force_authenticate(user=self.user)

        resp = self.client.get(reverse('benefits:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)

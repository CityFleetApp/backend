from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .factories import AccountingFactory


class TestAccountingViewSet(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()

    # Unauthorized user requests list of accounting services
    def test_login_required(self):
        resp = self.client.get(reverse('accounting:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # Authorized user requests list of accounting services
    def test_list(self):
        AccountingFactory.create_batch(10)
        self.client.login(username='test@example.com', password='password')
        resp = self.client.get(reverse('accounting:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)

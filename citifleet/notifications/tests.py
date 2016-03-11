from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .factories import NotificationFactory


class TestNotifications(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()

    def test_notification_list(self):
        NotificationFactory(message='Test', user=self.user)

        self.client.force_authenticate(self.user)
        resp = self.client.get(reverse('notifications:api-list'))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertTrue(resp.data[0]['unseen'])

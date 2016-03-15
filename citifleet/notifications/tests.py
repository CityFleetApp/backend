from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .models import Notification, MassNotification
from .factories import NotificationFactory


class TestNotifications(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()

    # User retrieves list of notifications
    def test_notification_list(self):
        NotificationFactory(message='Test', user=self.user)

        self.client.force_authenticate(self.user)
        resp = self.client.get(reverse('notifications:api-list'))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertTrue(resp.data[0]['unseen'])


class TestMassNotification(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()

    # Personal notifications is created after mass notification created
    def test_notifications_created(self):
        MassNotification.objects.create(title='Test', message='Message')

        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.get()
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.unseen, True)
        self.assertEqual(notification.message, 'Message')
        self.assertEqual(notification.title, 'Test')

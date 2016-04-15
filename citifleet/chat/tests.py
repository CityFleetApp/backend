from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .factories import MessageFactory, RoomFactory


class RoomTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()

    def test_empty_rooms_list(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('chat:rooms-list'))
        self.assertEqual(resp.data, [])

    def test_fetch_rooms(self):
        RoomFactory.create_batch(10, participants=[self.user])
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('chat:rooms-list') + '?page=1')
        self.assertEqual(len(resp.data), 10)

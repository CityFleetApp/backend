from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .models import Room
from .factories import RoomFactory, MessageFactory


class RoomTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.friend = UserFactory()
        self.user.friends.add(self.friend)

    def test_empty_rooms_list(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('chat:rooms-list'))
        self.assertEqual(resp.data, [])

    def test_fetch_rooms(self):
        RoomFactory.create_batch(10, participants=[self.user])
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('chat:rooms-list') + '?page=1')
        self.assertEqual(len(resp.data), 10)

    def test_create_room(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(reverse('chat:rooms-list'), data={'participants': [self.friend.id], 'name': 'Room'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['id'], Room.objects.get().id)

        resp = self.client.post(reverse('chat:rooms-list'), data={'participants': [self.friend.id], 'name': 'Room'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['id'], Room.objects.get().id)

    def test_room_ordering(self):
        room1, room2 = RoomFactory.create_batch(2, participants=[self.user])
        self.client.force_authenticate(user=self.user)

        resp = self.client.get(reverse('chat:rooms-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        self.assertEqual(resp.data[0]['id'], room2.id)

        MessageFactory(room=room1, author=self.user, text='text')
        resp = self.client.get(reverse('chat:rooms-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        self.assertEqual(resp.data[0]['id'], room1.id)

        MessageFactory(room=room2, author=self.user, text='text')
        resp = self.client.get(reverse('chat:rooms-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        self.assertEqual(resp.data[0]['id'], room2.id)

        MessageFactory(room=room2, author=self.user, text='text')
        MessageFactory(room=room2, author=self.user, text='text')
        MessageFactory(room=room2, author=self.user, text='text')

        resp = self.client.get(reverse('chat:rooms-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_invite_users(self):
        room = RoomFactory(participants=[self.user])
        self.client.force_authenticate(user=self.user)

        resp = self.client.patch(reverse('chat:rooms-detail', args=[room.id]),
                                 data={'participants': [self.friend.id, self.user.id]})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(self.friend in room.participants.all())
        self.assertTrue(self.user in room.participants.all())
        self.assertEqual(room.participants.count(), 2)

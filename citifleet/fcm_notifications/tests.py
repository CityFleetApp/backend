# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from copy import deepcopy

from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

from citifleet.users.factories import UserFactory
from citifleet.fcm_notifications.models import FCMDevice
from citifleet.fcm_notifications.serializers import FCMDeviceSerializer


class TestFCMDeviceAPI(APITestCase):

    def __init__(self, *args, **kwargs):
        super(TestFCMDeviceAPI, self).__init__(*args, **kwargs)
        self.device_registration_id = 'ejvVqlLhwq4:APA91bEZv4-77mteQ7FwKcIuMMTnBc_Xn5CSnYcLsrRUiuFO0qx8XaU--Mkplz_oWgxMvgmot74BRW7CLdSVew3mz_PrIkvoGUp9f_lokiYTJzTPx72cY6XMxpCcDe4Swx6ituC5mYUH'  # noqa
        self.device_id = 'f374bb015f9e15d3'
        self.device_create_data = {
            'registration_id': self.device_registration_id,
            'device_id': self.device_id,
            'active': True
        }

    def setUp(self):
        self.user = UserFactory(email='test@example.com')

    def test_login_required(self):
        resp = self.client.get(reverse('fcm_notifications:fcmdevice-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.post(reverse('fcm_notifications:fcmdevice-list'), data={})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.delete(reverse('fcm_notifications:fcmdevice-detail', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.post(reverse('fcm_notifications:fcmdevice-detail', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.patch(reverse('fcm_notifications:fcmdevice-detail', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def _create_device(self):
        resp = self.client.post(reverse('fcm_notifications:fcmdevice-list'), data=self.device_create_data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FCMDevice.objects.count(), 1)
        return resp

    def test_device_create_endpoint(self):
        self.client.force_authenticate(user=self.user)
        resp = self._create_device()
        device = FCMDevice.objects.get(registration_id=self.device_registration_id)
        self.assertEqual(device.registration_id, self.device_registration_id)
        self.assertEqual(device.device_id, self.device_id)
        self.assertEqual(device.user, self.user)
        self.assertEqual(device.device_os, FCMDevice.DEVICE_OS_CHOICES.android)
        self.assertTrue(device.active)
        self.assertEqual(resp.data, FCMDeviceSerializer(device).data)

    def test_device_with_ios_os_create(self):
        self.client.force_authenticate(user=self.user)
        data = deepcopy(self.device_create_data)
        data['device_os'] = FCMDevice.DEVICE_OS_CHOICES.ios
        resp = self.client.post(reverse('fcm_notifications:fcmdevice-list'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        device = FCMDevice.objects.get(registration_id=self.device_registration_id)
        self.assertEqual(FCMDevice.objects.count(), 1)
        self.assertEqual(device.registration_id, self.device_registration_id)
        self.assertEqual(device.device_id, self.device_id)
        self.assertEqual(device.user, self.user)
        self.assertEqual(device.device_os, FCMDevice.DEVICE_OS_CHOICES.ios)
        self.assertTrue(device.active)

    def test_device_unable_to_create_duplicates(self):
        self.client.force_authenticate(user=self.user)
        self._create_device()
        resp = self.client.post(reverse('fcm_notifications:fcmdevice-list'), data=self.device_create_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FCMDevice.objects.count(), 1)

    def test_device_list_endpoint(self):
        self.client.force_authenticate(user=self.user)
        self._create_device()
        resp = self.client.get(reverse('fcm_notifications:fcmdevice-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data, FCMDeviceSerializer(FCMDevice.objects.all(), many=True).data)

    def test_device_remove_endpoint(self):
        self.client.force_authenticate(user=self.user)
        self._create_device()
        resp = self.client.delete(reverse('fcm_notifications:fcmdevice-detail', args=[self.device_registration_id]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FCMDevice.objects.count(), 0)

    def test_device_patch_endpoint(self):
        self.client.force_authenticate(user=self.user)
        self._create_device()
        resp = self.client.patch(
            reverse('fcm_notifications:fcmdevice-detail', args=[self.device_registration_id]),
            data={'active': False}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        device = FCMDevice.objects.get(registration_id=self.device_registration_id)
        self.assertFalse(device.active)
        self.assertEqual(resp.data, FCMDeviceSerializer(device).data)

    def test_device_get_endpoint(self):
        self.client.force_authenticate(user=self.user)
        self._create_device()
        resp = self.client.get(reverse('fcm_notifications:fcmdevice-detail', args=[self.device_registration_id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        device = FCMDevice.objects.get(registration_id=self.device_registration_id)
        self.assertEqual(resp.data, FCMDeviceSerializer(device).data)

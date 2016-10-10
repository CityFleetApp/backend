# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import viewsets, permissions

from citifleet.fcm_notifications.models import FCMDevice
from citifleet.fcm_notifications.serializers import FCMDeviceSerializer


class FCMDeviceViewSet(viewsets.ModelViewSet):
    lookup_field = 'registration_id'
    permission_classes = (permissions.IsAuthenticated, )
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

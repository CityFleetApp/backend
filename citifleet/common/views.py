# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from push_notifications.api.rest_framework import DeviceViewSetMixin, AuthorizedMixin
from rest_framework.viewsets import ModelViewSet

from citifleet.common.models import CustomAPNSDevice
from citifleet.common.serializers import APNSDeviceSerializer


class APNSDeviceViewSet(DeviceViewSetMixin, ModelViewSet):
    queryset = CustomAPNSDevice.objects.all()
    serializer_class = APNSDeviceSerializer


class APNSDeviceAuthorizedViewSet(AuthorizedMixin, APNSDeviceViewSet):
    pass

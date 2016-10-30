# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from citifleet.fcm_notifications.models import FCMDevice


class FCMDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = FCMDevice
        fields = ('id', 'name', 'registration_id', 'device_id', 'active', 'date_created', 'device_os', )
        read_only_fields = ('date_created', )
        extra_kwargs = {
            'active': {
                'default': True
            },
            'device_os': {
                'default': FCMDevice.DEVICE_OS_CHOICES.android
            }
        }

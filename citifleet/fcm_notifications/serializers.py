# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers

from citifleet.fcm_notifications.models import FCMDevice


class FCMDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = FCMDevice
        fields = ('id', 'name', 'registration_id', 'device_id', 'active', 'date_created', )
        read_only_fields = ('date_created', )
        extra_kwargs = {
            'active': {
                'default': True
            }
        }

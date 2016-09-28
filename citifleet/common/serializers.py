# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from push_notifications.fields import hex_re
from push_notifications.api.rest_framework import DeviceSerializerMixin
from rest_framework import serializers

from citifleet.common.models import CustomAPNSDevice


class APNSDeviceSerializer(serializers.ModelSerializer):

    class Meta(DeviceSerializerMixin.Meta):
        model = CustomAPNSDevice

    def validate_registration_id(self, value):
        if hex_re.match(value) is None or len(value) not in (64, 200):
            raise serializers.ValidationError('Registration ID (device token) is invalid')

        return value

    def save(self, **kwargs):
        if kwargs.get('user'):
            kwargs['is_development'] = kwargs['user'].is_development
        return super(APNSDeviceSerializer, self).save(**kwargs)

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from push_notifications.models import Device, APNSDeviceManager
from push_notifications.apns import apns_send_message


class CustomAPNSDevice(Device):
    device_id = models.UUIDField(
        verbose_name=_('Device ID'),
        blank=True,
        null=True,
        db_index=True,
        help_text='UDID / UIDevice.identifierForVendor()'
    )
    registration_id = models.CharField(
        verbose_name=_('Registration ID'),
        max_length=200,
        unique=True
    )
    is_development = models.BooleanField(
        verbose_name=_('Development?'),
        default=False,
    )
    objects = APNSDeviceManager()

    class Meta:
        verbose_name = _('APNS device')
        app_label = 'push_notifications'

    def send_message(self, message, **kwargs):
        return apns_send_message(registration_id=self.registration_id, alert=message, **kwargs)

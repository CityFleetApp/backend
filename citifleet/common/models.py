# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from push_notifications.models import Device
from push_notifications.apns import apns_send_message, apns_send_bulk_message


class APNSDeviceManager(models.Manager):
    def get_queryset(self):
        return APNSDeviceQuerySet(self.model)


class APNSDeviceQuerySet(models.query.QuerySet):
    def send_message(self, message, **kwargs):
        if self:
            res_dev, res_prod = None, None
            qs = self.filter(active=True).values_list('registration_id', flat=True)
            dev_reg_ids = list(qs.filter(is_development=True))
            prod_reg_ids = list(qs.filter(is_development=False))
            if dev_reg_ids:
                res_dev = apns_send_bulk_message(
                    registration_ids=dev_reg_ids,
                    alert=message,
                    certfile=settings.PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE_DEV'],
                    **kwargs
                )
            if prod_reg_ids:
                res_prod = apns_send_bulk_message(
                    registration_ids=prod_reg_ids,
                    alert=message,
                    certfile=settings.PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE'],
                    **kwargs
                )
            return res_dev, res_prod


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

    def send_message(self, message, **kwargs):
        certfile = settings.PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE']
        if self.is_development:
            certfile = settings.PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE_DEV']
        return apns_send_message(
            registration_id=self.registration_id,
            alert=message,
            certfile=certfile,
            **kwargs
        )

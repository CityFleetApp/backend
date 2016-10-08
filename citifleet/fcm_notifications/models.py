# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class FCMDevice(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
        blank=True,
    )
    active = models.BooleanField(
        verbose_name=_('Is active'), default=True,
        help_text=_('Inactive devices will not be sent notifications')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_created = models.DateTimeField(
        verbose_name=_('Creation date'),
        auto_now_add=True,
        null=True
    )
    device_id = models.CharField(
        verbose_name=_('Device ID'),
        max_length=50,
        db_index=True,
        help_text=_('UDID / UIDevice.identifierForVendor() or ANDROID_ID / TelephonyManager.getDeviceId() (always as hex)')  # noqa
    )
    registration_id = models.TextField(
        verbose_name=_('Registration ID'),
        unique=True
    )

    class Meta:
        verbose_name = _('FCM Device')

    def __str__(self):
        return self.name or str(self.device_id)

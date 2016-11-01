# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from model_utils.choices import Choices
from citifleet.fcm_notifications.tasks import send_push_notification_task
from citifleet.fcm_notifications.utils import NOTIFICATION_COLOR


class FCMDeviceManager(models.Manager):
    def get_queryset(self):
        return FCMDeviceQuerySet(self.model)


class FCMDeviceQuerySet(models.query.QuerySet):
    def send_push_notification(self, device_os=None, **kwargs):
        if self:
            qs = self
            if device_os:
                qs = qs.filter(device_os=device_os)

            if qs:
                if not kwargs.get('color'):
                    kwargs['color'] = NOTIFICATION_COLOR
                reg_ids = list(qs.filter(active=True).values_list('registration_id', flat=True))
                send_push_notification_task.delay(settings.FCM_SERVER_KEY, reg_ids, kwargs)


@python_2_unicode_compatible
class FCMDevice(models.Model):
    DEVICE_OS_CHOICES = Choices(
        'ios', 'ios', 'iOS',
        'android', 'android', 'Android',
    )

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
    device_os = models.CharField(
        verbose_name=_('Device OS'),
        max_length=50,
        choices=DEVICE_OS_CHOICES,
        default=DEVICE_OS_CHOICES.android,
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
    objects = FCMDeviceManager()

    class Meta:
        verbose_name = _('FCM Device')

    def __str__(self):
        return self.name or str(self.device_id)

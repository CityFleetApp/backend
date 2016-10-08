# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from citifleet.fcm_notifications.models import FCMDevice


def send_push_notifications(users, **kwargs):
    FCMDevice.objects.filter(user__in=users).send_push_notification(**kwargs)


def send_mass_push_notifications(**kwargs):
    FCMDevice.objects.all().send_push_notification(**kwargs)

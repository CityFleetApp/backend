# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from citifleet.fcm_notifications.models import FCMDevice

NOTIFICATION_COLOR = '#192c3b'


def send_push_notifications(users, **kwargs):
    FCMDevice.objects.filter(user__in=users).send_push_notification(**kwargs)


def send_mass_push_notifications(**kwargs):
    FCMDevice.objects.all().send_push_notification(**kwargs)


def update_fcmdevice_registration_id(old_registration_id, new_registration_id):
    if FCMDevice.objects.filter(registration_id=new_registration_id).exists():
        FCMDevice.objects.filter(registration_id=old_registration_id).delete()
    else:
        FCMDevice.objects.filter(registration_id=old_registration_id).update(registration_id=new_registration_id)


def remove_fcmdevice_registration_id(registration_id):
    FCMDevice.objects.filter(registration_id=registration_id).delete()

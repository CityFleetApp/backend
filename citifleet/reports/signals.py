# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.measure import D
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from constance import config
from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.signals import user_location_changed
from .models import Report


User = get_user_model()


@receiver(post_save, sender=Report)
def report_created_nearby(sender, instance, created, **kwargs):
    """ Send push notification to the drivers that are within VISIBLE_REPORTS_RADIUS to created report """
    if created:
        apns_message = {
            'report_created':
                {
                    'id': instance.id, 'lat': instance.location.x,
                    'lng': instance.location.y, 'report_type': instance.report_type
                }
        }
        gcm_message = {
            'action': 'added', 'id': instance.id, 'lat': instance.location.x,
            'lng': instance.location.y, 'report_type': instance.report_type
        }
        gcm_kwargs = {'message': gcm_message, }
        apns_kwargs = {'message': None, 'extra': apns_message}

        nearby_drivers = User.objects.filter(
            location__distance_lte=(instance.location, D(mi=config.TLC_PUSH_NOTIFICATION_RADIUS))
        )
        if instance.report_type == Report.TLC:
            message = _('TLC TRAP REPORTED {} miles away, tap here to see').format(config.TLC_PUSH_NOTIFICATION_RADIUS)
            gcm_kwargs = {
                'message': message,
                'extra': gcm_message
            }
            apns_kwargs = {
                'message': message,
                'extra': apns_message
            }

        GCMDevice.objects.filter(user__in=nearby_drivers, active=True).send_message(**gcm_kwargs)
        nearby_drivers_id = APNSDevice.objects.filter(user__in=nearby_drivers, active=True).values_list('id', flat=True)
        for i in xrange(0, len(nearby_drivers_id), 20):
            APNSDevice.objects.filter(id__in=nearby_drivers_id[i:i + 20]).send_message(**apns_kwargs)


@receiver(pre_delete, sender=Report)
def report_removed_nearby(sender, instance, **kwargs):
    """ Send push notification to the drivers that are within VISIBLE_REPORTS_RADIUS to removed report """
    nearby_drivers = User.objects.filter(
        location__distance_lte=(instance.location, D(mi=config.TLC_PUSH_NOTIFICATION_RADIUS))
    )
    push_message = {'action': 'removed', 'id': instance.id, 'lat': instance.location.x,
                    'lng': instance.location.y, 'report_type': instance.report_type}
    GCMDevice.objects.filter(user__in=nearby_drivers).send_message(push_message)

    apns_push = {'report_removed': {'id': instance.id, 'lat': instance.location.x, 'lng': instance.location.y,
                                    'report_type': instance.report_type}}

    nearby_drivers_id = APNSDevice.objects.filter(user__in=nearby_drivers).values_list('id', flat=True)
    for i in xrange(0, len(nearby_drivers_id), 20):
        APNSDevice.objects.filter(id__in=nearby_drivers_id[i:i + 20]).send_message(None, extra=apns_push)


@receiver(user_location_changed, sender=User)
def update_tlc_notifications(user, **kwargs):
    reports_withing_radius = Report.objects.filter(
        report_type=Report.TLC,
        location__distance_lte=(user.location, D(mi=config.TLC_PUSH_NOTIFICATION_RADIUS))
    )
    reports_to_notify = list(reports_withing_radius.exclude(
        pk__in=user.notified_reports.only('pk').values_list('id', flat=True)
    ))
    if reports_to_notify:
        message = _('TLC TRAPS REPORTED {} miles away, open CityFleet now to see')
        notification_type = 'near_tlc_report'
        android_push_msg = {'type': notification_type, }
        apns_push_msg = {'type': notification_type, }

        if len(reports_to_notify) == 1:
            message = _('TLC TRAP REPORTED {} miles away, tap here to see')
            report = reports_to_notify[0]
            report_data = {
                'report': {
                    'id': report.pk,
                    'lat': report.location.x,
                    'lng': report.location.y,
                    'report_type': report.report_type
                }
            }
            android_push_msg.update(report_data)
            apns_push_msg.update(report_data)

        message = message.format(config.TLC_PUSH_NOTIFICATION_RADIUS)
        GCMDevice.objects.filter(user=user, active=True).send_message(message=message, extra=android_push_msg)
        APNSDevice.objects.filter(user=user, active=True).send_message(message=message, extra=apns_push_msg)

    user.notified_reports.clear()
    user.notified_reports.add(*reports_withing_radius)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.gis.measure import D
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from constance import config

from citifleet.common.utils import send_gcm_push_notification, send_apns_push_notification
from citifleet.users.signals import user_location_changed
from citifleet.reports.models import Report


User = get_user_model()


@receiver(post_save, sender=Report)
def report_created_nearby(sender, instance, created, **kwargs):
    """
    Send notification about new report creation
    - in first part hidden push notifications are sent to every user that are online to update report's marks on map
    - in second part push notification about TLC in radius are sent to users that are within N miles
    """
    if created:
        apns_message = {
            'report_created': {
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

        driver_to_notify = User.objects.filter(location__isnull=False).exclude(pk=instance.user.pk)

        gcm_response = send_gcm_push_notification(driver_to_notify, gcm_kwargs)
        apns_response = send_apns_push_notification(driver_to_notify, apns_kwargs)

        if instance.report_type == Report.TLC:
            driver_withing_report = driver_to_notify.filter(
                location__distance_lte=(instance.location, D(mi=config.TLC_PUSH_NOTIFICATION_RADIUS))
            )
            message = _('TLC TRAP REPORTED {} miles away, tap here to see').format(config.TLC_PUSH_NOTIFICATION_RADIUS)
            gcm_kwargs = {
                'message': message,
                'extra': gcm_message
            }
            apns_kwargs = {
                'message': message,
                'sound': 'default',
                'extra': apns_message
            }
            gcm_response = send_gcm_push_notification(driver_withing_report, gcm_kwargs)
            apns_response = send_apns_push_notification(driver_withing_report, apns_kwargs)


@receiver(pre_delete, sender=Report)
def report_removed_nearby(sender, instance, **kwargs):
    """ Send hidden push notification to the all users to removed report mark from map """
    driver_to_notify = User.objects.filter(location__isnull=False)
    push_message = {
        'action': 'removed', 'id': instance.id, 'lat': instance.location.x,
        'lng': instance.location.y, 'report_type': instance.report_type,
    }
    apns_push = {
        'report_removed': {
            'id': instance.id, 'report_type': instance.report_type,
            'lat': instance.location.x, 'lng': instance.location.y,
        }
    }
    gcm_response = send_gcm_push_notification(driver_to_notify, {'message': push_message})
    apns_response = send_apns_push_notification(driver_to_notify, {'message': None, 'extra': apns_push})


@receiver(user_location_changed, sender=User)
def update_tlc_notifications(user, **kwargs):
    """
    Send push notification for user if new TLC reports were found
    within radius config.TLC_PUSH_NOTIFICATION_RADIUS
    """
    if not user.location:
        return

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

        gcm_response = send_gcm_push_notification([user, ], {'message': message, 'extra': android_push_msg})
        apns_response = send_apns_push_notification(
            [user, ],
            {
                'message': message,
                'sound': 'default',
                'extra': apns_push_msg
            }
        )

    user.notified_reports.clear()
    user.notified_reports.add(*reports_withing_radius)

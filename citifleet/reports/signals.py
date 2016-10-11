# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.contrib.auth import get_user_model
from django.contrib.gis.measure import D
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from constance import config

from citifleet.fcm_notifications.utils import send_push_notifications
from citifleet.users.signals import user_location_changed
from citifleet.reports.models import Report

logger = logging.getLogger('cityfleet.push_notifications')
User = get_user_model()


@receiver(post_save, sender=Report)
def report_created_nearby(sender, instance, created, **kwargs):
    """
    Send notification about new report creation
    - in first part hidden push notifications are sent to every user that are online to update report's marks on map
    - in second part push notification about TLC in radius are sent to users that are within N miles
    """
    if created:
        logger.info('New report created with id \'%s\' and location \'%s\' by user \'%s\'',
                    instance.pk, instance.location, instance.user)

        notification_data = {
            'notification_type': 'report_created',
            'report': {
                'id': instance.id,
                'lat': instance.location.x,
                'lng': instance.location.y,
                'type': instance.report_type
            }
        }
        driver_to_notify = User.objects.filter(location__isnull=False).exclude(pk=instance.user.pk)
        logger.debug('Send data notification to users %s', driver_to_notify)
        send_push_notifications(driver_to_notify, data_message=notification_data)

        if instance.report_type == Report.TLC:
            logger.debug('This is TLC report. Need to send additional push notification.')
            driver_withing_report = driver_to_notify.filter(
                location__distance_lte=(instance.location, D(mi=config.TLC_PUSH_NOTIFICATION_RADIUS))
            )
            logger.debug('Send notification to \'%s\' users', driver_withing_report)
            message = _('TLC TRAP REPORTED {} miles away, tap here to see').format(config.TLC_PUSH_NOTIFICATION_RADIUS)

            notification_data['notification_type'] = 'tlc_report_withing_radius'
            send_push_notifications(
                driver_withing_report,
                message_title=message,
                message_body=message,
                data_message=notification_data,
                sound='default',
            )
        logger.info('Report post_save signal processed')


@receiver(pre_delete, sender=Report)
def report_removed_nearby(sender, instance, **kwargs):
    """ Send hidden push notification to the all users to removed report mark from map """
    logger.info('Report with id \'%s\' was deleted. Send hidden notification to all users', instance.pk)
    driver_to_notify = User.objects.filter(location__isnull=False)
    notification_data = {
        'notification_type': 'report_removed',
        'report': {
            'id': instance.id,
            'lat': instance.location.x,
            'lng': instance.location.y,
            'type': instance.report_type
        }
    }
    send_push_notifications(
        driver_to_notify,
        data_message=notification_data
    )
    logger.info('Report pre_delete signal processed')


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
    reports_to_notify = reports_withing_radius.exclude(
        pk__in=user.notified_reports.only('pk').values_list('id', flat=True)
    )
    reports_to_notify_count = reports_to_notify.count()
    if reports_to_notify_count:
        logger.info('User location changed signal with reports to notify. Found \'%s\' reports',
                    reports_to_notify_count)
        notification_data = {
            'notification_type': 'tlc_report_withing_radius',
        }

        message = _('TLC TRAPS REPORTED {} miles away, open CityFleet now to see')
        if reports_to_notify_count == 1:
            message = _('TLC TRAP REPORTED {} miles away, tap here to see')
            report = reports_to_notify[0]
            notification_data['report'] = {
                'id': report.pk,
                'lat': report.location.x,
                'lng': report.location.y,
                'type': report.report_type
            }
        message = message.format(config.TLC_PUSH_NOTIFICATION_RADIUS)
        send_push_notifications(
            [user, ],
            message_title=message,
            message_body=message,
            data_message=notification_data,
            sound='default',
        )
        logger.info('User location changed signal with reports to notify processed')

    user.notified_reports.clear()
    user.notified_reports.add(*reports_withing_radius)

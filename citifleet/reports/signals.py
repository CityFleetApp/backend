# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.contrib.auth import get_user_model
from django.contrib.gis.measure import D
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from constance import config

from citifleet.common.utils import send_gcm_push_notification, send_apns_push_notification
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
        logger.debug('Send hidden notification to users')
        gcm_response = send_gcm_push_notification(driver_to_notify, gcm_kwargs)
        logger.debug('GCM response: %s', gcm_response)
        apns_response = send_apns_push_notification(driver_to_notify, apns_kwargs)
        logger.debug('APNS response: %s', apns_response)

        if instance.report_type == Report.TLC:
            logger.debug('This is TLC report. Need to send additional push notification.')
            driver_withing_report = driver_to_notify.filter(
                location__distance_lte=(instance.location, D(mi=config.TLC_PUSH_NOTIFICATION_RADIUS))
            )
            logger.debug('Send notification to \'%s\' users', driver_withing_report)
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
            logger.debug('GCM response: %s', gcm_response)
            apns_response = send_apns_push_notification(driver_withing_report, apns_kwargs)
            logger.debug('APNS response: %s', apns_response)
        logger.info('Report post_save signal processed')


@receiver(pre_delete, sender=Report)
def report_removed_nearby(sender, instance, **kwargs):
    """ Send hidden push notification to the all users to removed report mark from map """
    logger.info('Report with id \'%s\' was deleted. Send hidden notification to all users', instance.pk)
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
    logger.debug('GCM response: %s', gcm_response)

    apns_response = send_apns_push_notification(driver_to_notify, {'message': None, 'extra': apns_push})
    logger.debug('APNS response: %s', apns_response)
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

        message = _('TLC TRAPS REPORTED {} miles away, open CityFleet now to see')
        notification_type = 'near_tlc_report'
        android_push_msg = {'type': notification_type, }
        apns_push_msg = {'type': notification_type, }

        if reports_to_notify_count == 1:
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
        logger.debug('GCM response: %s', gcm_response)

        apns_response = send_apns_push_notification(
            [user, ],
            {
                'message': message,
                'sound': 'default',
                'extra': apns_push_msg
            }
        )
        logger.debug('APNS response: %s', apns_response)
        logger.info('User location changed signal with reports to notify processed')

    user.notified_reports.clear()
    user.notified_reports.add(*reports_withing_radius)

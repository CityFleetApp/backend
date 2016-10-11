# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from citifleet.fcm_notifications.utils import send_push_notifications
from citifleet.users.models import User


class NotificationBase(models.Model):
    title = models.CharField(_('title'), max_length=255)
    message = models.CharField(_('message'), max_length=255)
    category = models.CharField(_('category'), max_length=50)
    ref_type = models.CharField(_('type'), max_length=255, blank=True)
    ref_id = models.PositiveIntegerField(blank=True, null=True)

    @property
    def to_dict(self):
        return {'title': self.title, 'message': self.message, 'category': self.category}

    class Meta:
        abstract = True


class MassNotification(NotificationBase):
    created = models.DateField(_('created'), auto_now_add=True)

    def __unicode__(self):
        return '{}, {}'.format(self.title, self.message)

    class Meta:
        verbose_name = _('Mass notification')
        verbose_name_plural = _('Mass notifications')


class Notification(NotificationBase):
    user = models.ForeignKey(User)
    unseen = models.BooleanField(_('unseen'), default=True)
    created = models.DateField(_('created'), auto_now_add=True)

    def __unicode__(self):
        return '{}, {}'.format(self.title, self.message)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')


class NotificationTemplate(NotificationBase):
    NEW_BENEFIT = 1
    DOCUMENT_EXPIRED = 2
    DOCUMENT_VERIFIED = 3
    REPORT_CREATED = 4
    JOBOFFER_CREATED = 5
    CAR_CREATED = 6
    GENERAL_GOODS_CREATED = 7

    NOTIFICATION_CHOICES = (
        (NEW_BENEFIT, _('New Benefit')),
        (DOCUMENT_EXPIRED, _('Document Expired')),
        (DOCUMENT_VERIFIED, _('Document Verified')),
        (JOBOFFER_CREATED, _('Job Offer Created')),
        (CAR_CREATED, _('Car for Sale/Rent Created')),
        (GENERAL_GOODS_CREATED, _('Genera Goods created')),
    )

    PUSH_TYPES = {
        NEW_BENEFIT: 'benefit_created',
        DOCUMENT_EXPIRED: 'document_expired',
        DOCUMENT_VERIFIED: 'document_verified',
        JOBOFFER_CREATED: 'offer_created',
        CAR_CREATED: 'car_created',
        GENERAL_GOODS_CREATED: 'goods_created',
    }

    type = models.PositiveSmallIntegerField(_('type'), choices=NOTIFICATION_CHOICES)
    enabled = models.BooleanField(_('enabled'), default=True)

    def __unicode__(self):
        return self.get_type_display()

    @staticmethod
    def send_notification(type, drivers=None, **extra):
        try:
            template_dict = NotificationTemplate.objects.get(type=type, enabled=True).to_dict
        except NotificationTemplate.DoesNotExist:
            return

        if drivers is None:
            drivers = User.with_notifications.all()

        if type == NotificationTemplate.JOBOFFER_CREATED:
            template_dict['ref_type'] = NotificationTemplate.PUSH_TYPES[type]
            template_dict['ref_id'] = extra.get('id')
            template_dict['title'] = 'Job Offer "{}" created'.format(extra.get('title'))

        Notification.objects.bulk_create([Notification(user=user, **template_dict) for user in drivers])
        send_push_notifications(
            drivers,
            message_title=template_dict['title'],
            sound='default',
            data_message={
                'notification_type': NotificationTemplate.PUSH_TYPES[type],
                'notification': extra,
            }
        )

    class Meta:
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')

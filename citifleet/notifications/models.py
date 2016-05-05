from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.models import User


class NotificationBase(models.Model):
    title = models.CharField(_('title'), max_length=255)
    message = models.CharField(_('message'), max_length=255)
    category = models.CharField(_('category'), max_length=50)

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

        Notification.objects.bulk_create(
                [Notification(user=user, **template_dict)
                 for user in drivers])

        push_message = {'type': NotificationTemplate.PUSH_TYPES[type],
                        'title': template_dict['title']}
        push_message.update(extra)

        GCMDevice.objects.filter(user__in=drivers).send_message(push_message)

        alert_message = template_dict['title']
        APNSDevice.objects.filter(user__in=drivers).send_message(
            alert_message, sound='defauld', extra={push_message['type']: extra})

    class Meta:
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')

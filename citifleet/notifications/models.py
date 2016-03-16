from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from citifleet.users.models import User


class MassNotification(models.Model):
    title = models.CharField(_('title'), max_length=255)
    message = models.CharField(_('message'), max_length=255)
    created = models.DateField(_('created'), auto_now_add=True)

    def __unicode__(self):
        return '{}, {}'.format(self.title, self.message)

    class Meta:
        verbose_name = _('Mass notification')
        verbose_name_plural = _('Mass notifications')


class Notification(models.Model):
    created = models.DateField(_('created'), auto_now_add=True)
    title = models.CharField(_('title'), max_length=255)
    message = models.CharField(_('message'), max_length=255)
    user = models.ForeignKey(User)
    unseen = models.BooleanField(_('unseen'), default=True)

    def __unicode__(self):
        return '{}, {}'.format(self.title, self.message)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

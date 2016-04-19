from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Room(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='participants',
                                          related_name='participants')
    created = models.DateTimeField(_('Created'), auto_now_add=True)

    def __unicode__(self):
        return ','.join([p.full_name for p in self.participants.all()])

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')


class Message(models.Model):
    text = models.TextField(_('Message'))
    room = models.ForeignKey(Room, verbose_name=_('Room'), related_name='messages')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='author', related_name='messages')
    created = models.DateTimeField(_('Created'), auto_now_add=True)

    def __unicode__(self):
        return self.text[:20]

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

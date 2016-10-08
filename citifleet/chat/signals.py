# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F

from citifleet.fcm_notifications.utils import send_push_notifications
from citifleet.common.utils import get_full_path

from .models import Message, UserRoom
from .serializers import MessageSerializer


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    """ Send push notification to room participants """
    if created:
        message_data = MessageSerializer(instance).data
        if instance.image:
            message_data['image'] = get_full_path(instance.image.url)

        alert_message = u'{} {}'.format(instance.author.username, instance.text)
        notification_data = {
            'notification_type': 'message_created',
            'message': message_data
        }
        send_push_notifications(
            instance.room.participants.all(),
            message_title=alert_message,
            sound='default',
            message_data=notification_data,
        )
        participants = instance.room.participants.exclude(id=instance.author.id)
        UserRoom.objects.filter(room=instance.room, user__in=participants).update(unseen=F('unseen') + 1)

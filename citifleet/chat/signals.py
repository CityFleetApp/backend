# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from citifleet.fcm_notifications.utils import send_push_notifications
from citifleet.fcm_notifications.models import FCMDevice
from citifleet.common.utils import get_full_path, PUSH_NOTIFICATION_MESSAGE_TYPES
from citifleet.chat.models import Message, UserRoom
from citifleet.chat.serializers import MessageSerializer


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    """ Send push notification to room participants """
    if created:
        message_data = MessageSerializer(instance).data
        if instance.image:
            message_data['image'] = get_full_path(instance.image.url)

        notification_data = {
            'notification_type': PUSH_NOTIFICATION_MESSAGE_TYPES.message_created,
            'message': message_data
        }
        send_push_notifications(
            instance.room.participants.all(),
            device_os=FCMDevice.DEVICE_OS_CHOICES.android,
            sound='default',
            data_message=notification_data,
        )

        send_push_notifications(
            instance.room.participants.all(),
            device_os=FCMDevice.DEVICE_OS_CHOICES.ios,
            sound='default',
            message_body='%s: %s' % (instance.author.username.title(), instance.text),
            data_message=notification_data,
        )
        participants = instance.room.participants.exclude(id=instance.author.id)
        UserRoom.objects.filter(room=instance.room, user__in=participants).update(unseen=F('unseen') + 1)

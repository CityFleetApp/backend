from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F

from push_notifications.models import GCMDevice

from citifleet.common.serializers import CustomAPNSDevice as APNSDevice
from citifleet.common.utils import get_full_path

from .models import Message, UserRoom
from .serializers import MessageSerializer


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    """ Send push notification to room participants """
    if created:
        push_message = {'type': 'receive_message'}
        push_message.update(MessageSerializer(instance).data)
        if instance.image:
            push_message['image'] = get_full_path(instance.image.url)

        response = GCMDevice.objects.filter(
            user__in=instance.room.participants.all(),
            active=True
        ).send_message(push_message)

        alert_message = u'{} {}'.format(instance.author.username, instance.text)
        response = APNSDevice.objects.filter(
            user__in=instance.room.participants.all(),
            active=True
        ).send_message(
            alert_message,
            sound='default',
            extra={
                'receive_message': {
                    'room_id': instance.room.id,
                    'avatar': instance.author.avatar_url()
                }
            }
        )

        participants = instance.room.participants.exclude(id=instance.author.id)
        UserRoom.objects.filter(room=instance.room, user__in=participants).update(unseen=F('unseen') + 1)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F

from push_notifications.models import APNSDevice, GCMDevice

from .models import Message, UserRoom
from .serializers import MessageSerializer, UserRoomSerializer


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    '''
    Send push notification to room participants
    '''
    if created:
        push_message = {'type': 'receive_message'}
        push_message.update(MessageSerializer(instance).data)

        GCMDevice.objects.filter(user__in=instance.room.participants.all()).send_message(push_message)
        APNSDevice.objects.filter(user__in=instance.room.participants.all()).send_message(push_message)

        participants = instance.room.participants.exclude(id=instance.author.id)
        UserRoom.objects.filter(room=instance.room, user__in=participants).update(unseen=F('unseen') + 1)


@receiver(post_save, sender=UserRoom)
def room_invitation(sender, instance, created, **kwargs):
    '''
    Send push notification to new room participants
    '''
    if created:
        push_message = {'type': 'room_invitation'}
        push_message.update(UserRoomSerializer(instance).data)

        GCMDevice.objects.filter(user__in=instance.room.participants.all()).send_message(push_message)
        APNSDevice.objects.filter(user__in=instance.room.participants.all()).send_message(push_message)

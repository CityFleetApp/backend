from django.db.models.signals import post_save
from django.dispatch import receiver

from push_notifications.models import APNSDevice, GCMDevice

from .models import Message, Room
from .serializers import MessageSerializer, RoomSerializer


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    '''
    Send push notification to the drivers when new marketplace item is created
    '''
    if created:
        push_message = {'type': 'receive_message'}
        push_message.update(MessageSerializer(instance).data)

        GCMDevice.objects.filter(user__in=instance.room.participants.all()).send_message(push_message)
        APNSDevice.objects.filter(user__in=instance.room.participants.all()).send_message(push_message)


@receiver(post_save, sender=Room)
def room_invitation(sender, instance, created, **kwargs):
    '''
    Send push notification to the drivers when new marketplace item is created
    '''
    if created:
        push_message = {'type': 'room_invitation'}
        push_message.update(RoomSerializer(instance).data)

        GCMDevice.objects.filter(user__in=instance.participants.all()).send_message(push_message)
        APNSDevice.objects.filter(user__in=instance.participants.all()).send_message(push_message)

from django.db.models.signals import post_save
from django.dispatch import receiver

from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.models import User

from .models import MassNotification, Notification


@receiver(post_save, sender=MassNotification)
def create_personal_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.bulk_create(
            [Notification(user=user, message=instance.message, title=instance.title) for user in User.objects.all()])


@receiver(post_save, sender=Notification)
def send_push_on_notification_create(sender, instance, created, **kwargs):
    if created:
        GCMDevice.objects.filter(user=instance.user).send_message(instance.title)
        APNSDevice.objects.filter(user=instance.user).send_message(instance.title)

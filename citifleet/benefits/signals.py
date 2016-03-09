from django.db.models.signals import post_save
from django.dispatch import receiver

from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.models import User
from citifleet.notifications.models import Notification, NotificationTemplate

from .models import Benefit


@receiver(post_save, sender=Benefit)
def send_push_on_benefit_created(sender, instance, created, **kwargs):
    '''
    Create notification when new benefit created
    '''
    if created:
        try:
            template_dict = NotificationTemplate.objects.get(
                type=NotificationTemplate.NEW_BENEFIT, enabled=True).to_dict()
        except NotificationTemplate.DoesNotExist:
            pass
        else:
            Notification.objects.bulk_create(
                [Notification(user=user, **template_dict)
                 for user in User.with_notifications.all()])

            GCMDevice.objects.filter(user__in=User.with_notifications.all()).send_message(instance.title)
            APNSDevice.objects.filter(user__in=User.with_notifications.all()).send_message(instance.title)

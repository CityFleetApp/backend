from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.gis.measure import D
from django.conf import settings

from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.models import User
from citifleet.notifications.models import NotificationTemplate

from .models import JobOffer, GeneralGood, Car


@receiver(post_save, sender=JobOffer)
def joboffer_created(sender, instance, created, **kwargs):
    '''
    Send push notification to the drivers when new marketplace item is created
    '''
    if created:
        try:
            notification = NotificationTemplate.objects.get(type=JOBOFFER_CREATED, enabled=True).to_dict()
        except NotificationTemplate.DoesNotExist:
            return
        else:
            Notification.objects.bulk_create(
                [Notification(user=user, **template_dict)
                 for user in User.with_notifications.all()])

            GCMDevice.objects.filter(user__in=drivers).send_message(push_message)
            APNSDevice.objects.filter(user__in=drivers).send_message(push_message)

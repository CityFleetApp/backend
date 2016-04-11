from django.db.models.signals import post_save
from django.dispatch import receiver

from citifleet.notifications.models import NotificationTemplate

from .models import JobOffer, GeneralGood, Car


@receiver(post_save, sender=JobOffer)
def joboffer_created(sender, instance, created, **kwargs):
    '''
    Send push notification to the drivers when new marketplace item is created
    '''
    if created:
        extra = {'id': instance.id}
        NotificationTemplate.send_notification(NotificationTemplate.JOBOFFER_CREATED, **extra)


@receiver(post_save, sender=GeneralGood)
def goods_created(sender, instance, created, **kwargs):
    if created:
        extra = {'id': instance.id}
        NotificationTemplate.send_notification(NotificationTemplate.GENERAL_GOODS_CREATED, **extra)


@receiver(post_save, sender=Car)
def car_created(sender, instance, created, **kwargs):
    if created:
        extra = {'id': instance.id, 'rent': instance.rent}
        NotificationTemplate.send_notification(NotificationTemplate.CAR_CREATED, **extra)

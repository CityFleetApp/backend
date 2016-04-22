from django.db.models.signals import post_save
from django.dispatch import receiver

from citifleet.notifications.models import NotificationTemplate

from .models import Benefit


@receiver(post_save, sender=Benefit)
def send_push_on_benefit_created(sender, instance, created, **kwargs):
    '''
    Create notification when new benefit created
    '''
    if created:
        extra = {'id': instance.id}
        NotificationTemplate.send_notification(NotificationTemplate.NEW_BENEFIT, extra)

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from push_notifications.models import APNSDevice, GCMDevice


@receiver(pre_delete, sender=GCMDevice)
@receiver(pre_delete, sender=APNSDevice)
def remove_user_location_on_logout(sender, instance, **kwargs):
    '''
    Send push notification to the drivers that are within VISIBLE_REPORTS_RADIUS to created
    report
    '''
    instance.user.location = None
    instance.user.save()


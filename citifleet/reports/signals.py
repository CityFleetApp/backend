from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.gis.measure import D
from django.conf import settings

from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.models import User

from .models import Report


@receiver(post_save, sender=Report)
def report_created_nearby(sender, instance, created, **kwargs):
    '''
    Send push notification to the drivers that are within VISIBLE_REPORTS_RADIUS to created
    report
    '''
    if created:
        nearby_drivers = User.objects.filter(
            location__distance_lte=(instance.location, D(settings.VISIBLE_REPORTS_RADIUS)))
        push_message = {'action': 'added', 'id': instance.id, 'location': instance.location,
                        'type': instance.report_type}
        GCMDevice.objects.filter(user__in=nearby_drivers).send_message(push_message)
        APNSDevice.objects.filter(user__in=nearby_drivers).send_message(push_message)


@receiver(pre_delete, sender=Report)
def report_removed_nearby(sender, instance, **kwargs):
    '''
    Send push notification to the drivers that are within VISIBLE_REPORTS_RADIUS to
    removed report
    '''
    nearby_drivers = User.objects.filter(
            location__distance_lte=(instance.location, D(settings.VISIBLE_REPORTS_RADIUS)))
    push_message = {'action': 'removed', 'id': instance.id, 'location': instance.location,
                    'type': instance.report_type}
    GCMDevice.objects.filter(user__in=nearby_drivers).send_message(push_message)
    APNSDevice.objects.filter(user__in=nearby_drivers).send_message(push_message)

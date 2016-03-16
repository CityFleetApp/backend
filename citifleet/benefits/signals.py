from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from citifleet.users.models import User
from citifleet.notifications.models import Notification

from .models import Benefit


@receiver(post_save, sender=Benefit)
def send_push_on_benefit_created(sender, instance, created, **kwargs):
    '''
    Send push notification to the drivers that are within VISIBLE_REPORTS_RADIUS to created
    report
    '''
    if created:
        Notification.objects.bulk_create(
            [Notification(user=user, message=_('Check out new benefit'), title=_('New Benefit created'))
             for user in User.objects.all()])

from datetime import timedelta

from django.utils import timezone
from django.utils.translation import ugettext as _

from celery.task import periodic_task
from citifleet.notifications.models import Notification

from .models import Document


@periodic_task(run_every=timedelta(days=1))
def document_expired_notification():
    """ Send notification when document becomes expired """
    expiry_date = timezone.now() - timedelta(days=1)
    users_to_notify = Document.objects.filter(expiry_date=expiry_date.date()).values('user', flat=True)
    for user in users_to_notify:
        Notification.objects.create(
            user=user, title=_('Document has expired'), message=_('Document has expired'))

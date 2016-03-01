from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from celery.task import periodic_task

from .models import Report


@periodic_task(run_every=timedelta(minutes=1))
def delete_unconfirmed_reports():
    '''
    Remove reports that were not confirmed more than one hour
    '''
    check_time = timezone.now() - timedelta(minutes=settings.AUTOCLOSE_INTERVAL)
    Report.objects.filter(updated__lte=check_time).delete()

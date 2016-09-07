# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from datetime import timedelta

from celery.task import periodic_task

from django.contrib.auth import get_user_model
from django.utils import timezone as tz

User = get_user_model()


@periodic_task(run_every=timedelta(minutes=1))
def remove_expired_users_locations():
    """ Remove user's locations that were changed more than 2 minutes ago """
    expired_time = tz.now() - tz.timedelta(minutes=2)
    User.objects.filter(datetime_location_changed__lte=expired_time).update(
        location=False,
        datetime_location_changed=None
    )

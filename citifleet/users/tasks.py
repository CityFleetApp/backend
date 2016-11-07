# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from celery.task import periodic_task

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.utils import timezone as tz

from citifleet.taskapp.celery import app

User = get_user_model()


@periodic_task(run_every=timedelta(minutes=1))
def remove_expired_users_locations():
    """ Remove user's locations that were changed more than 2 minutes ago """
    expired_time = tz.now() - tz.timedelta(minutes=2)
    User.objects.filter(
        models.Q(datetime_location_changed__isnull=True) |
        models.Q(datetime_location_changed__lte=expired_time)
    ).filter(location__isnull=False).update(location=None, datetime_location_changed=None)


@app.task
def send_email_task(subject, message, recipients_emails, from_email=None, **kwargs):
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    msg = EmailMessage(subject, message, from_email, recipients_emails)
    msg.send(fail_silently=True)

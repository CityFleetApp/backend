# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from constance import config

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

user_location_changed = Signal(providing_args=['user', ])
User = get_user_model()


@receiver(post_save, sender=User)
def send_push_on_benefit_created(sender, instance, created, **kwargs):
    """ Send welcome email after registration """
    if created:
        context = {
            'username': instance.username,
            'name': instance.full_name,
        }

        subject = config.WELCOME_EMAIL_SUBJECT % context
        message = config.WELCOME_EMAIL_MESSAGE % context
        instance.email_user(subject, message, from_email=None)

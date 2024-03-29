# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import re
import string

from urllib2 import HTTPError

from model_utils.choices import Choices
from constance import config
from sodapy import Socrata

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

USERNAME_REGEX = re.compile(r'^[\w.@+-]+$', re.UNICODE)

PUSH_NOTIFICATION_MESSAGE_TYPES = Choices(
    ('message_created', 'message_created', _('Notification about new message in chat')),
    ('offer_covered', 'offer_covered', _('Notification about job offer accepted')),
    ('job_offer_completed', 'job_offer_completed', _('Notification about job offer completion')),
    ('report_created', 'report_created', _('Notification about new report created')),
    ('report_removed', 'report_removed', _('Notification about new report remove')),
    ('tlc_report_withing_radius', 'tlc_report_withing_radius', _('Notification about TLC within radius')),
    ('mass_notification', 'mass_notification', _('Mass notification type')),
    ('document_expire', 'document_expire', _('Notifications about documents expiration')),
)


def validate_license(license_number, full_name):
    """
    Verifies full driver's name and license number via SODA API.
    Returns True if license is verified, otherwise - False.
    In DEBUG mode always returns False.
    """
    if settings.DEBUG or not config.SODA_CHECK_ENABLED:
        return True
    else:
        client = Socrata(settings.TLC_URL, settings.APP_TOKEN)
        try:
            fhv_resp = client.get(settings.TLC_FOR_HIRE_DRIVERS,
                                  license_number=license_number, q=full_name)
            medallion_resp = client.get(settings.TLC_MEDALLION,
                                        license_number=license_number, q=full_name)
        except HTTPError:
            return False
        else:
            return len(fhv_resp) > 0 or len(medallion_resp) > 0


def get_protocol():
    if settings.SECURE_SSL_REDIRECT:
        return 'https://'
    else:
        return 'http://'


def get_full_path(relative_url):
    return '{}{}{}'.format(get_protocol(), Site.objects.get_current().domain, relative_url)


def generate_username(fullname):
    User = get_user_model()
    if not fullname.strip():
        return ''

    new_username = ''
    try_count = 0
    while not new_username and try_count < 10:
        fullname_upper = fullname.strip().upper()
        name_parts = [p for p in fullname_upper.split(' ') if p]
        if len(name_parts) > 1:
            for name_part in name_parts:
                new_username += name_part[0]
        else:
            new_username += len(fullname_upper) > 2 and fullname_upper[:2] or fullname_upper

        new_username += ''.join([random.choice(string.digits) for _ in range(4)])
        if User.objects.filter(username__exact=new_username).exists():
            new_username = ''
            try_count += 1

    if not new_username:
        allowed_chars = ''.join((string.uppercase, string.digits))
        new_username = ''.join(random.choice(allowed_chars) for _ in range(10))

    return new_username


def validate_username(username):
    if not USERNAME_REGEX.match(username):
        raise forms.ValidationError(
            _('Enter a valid username. This value may contain only letters, numbers ' 'and @/./+/-/_ characters.')
        )

    User = get_user_model()
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        return username
    raise forms.ValidationError(_('This username is already taken. Please choose another.'))

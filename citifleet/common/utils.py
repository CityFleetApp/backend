# -*- coding: utf-8 -*-

import random
import string
from urllib2 import HTTPError

from django.conf import settings
from django.contrib.sites.models import Site

from constance import config
from sodapy import Socrata


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
    from django.contrib.auth import get_user_model

    User = get_user_model()
    if not fullname.strip():
        return ''

    new_username = ''
    try_count = 0
    while not new_username and try_count < 10:
        fullname_upper = fullname.strip().upper()
        name_parts = fullname_upper.split(' ')
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
        allowed_chars = ''.join((string.lowercase, string.uppercase, string.digits))
        new_username = ''.join(random.choice(allowed_chars) for _ in range(10))

    return new_username

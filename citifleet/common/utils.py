from urllib2 import HTTPError

from django.conf import settings

from sodapy import Socrata


def validate_license(license_number, full_name):
    '''
    Verifies full driver's name and license number via SODA API.
    Returns True if license is verified, otherwise - False.
    In DEBUG mode always returns False.
    '''
    if settings.DEBUG:
        return True
    else:
        client = Socrata(settings.TLC_URL, settings.APP_TOKEN)
        try:
            resp = client.get(settings.TLC_OPEN_DATA_ID,
                              license_number=license_number, q=full_name)
        except HTTPError:
            return False
        else:
            return len(resp) > 0


def get_protocol():
    if settings.SECURE_SSL_REDIRECT:
        return 'https://'
    else:
        return 'http://'

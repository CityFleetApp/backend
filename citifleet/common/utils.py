from urllib2 import HTTPError

from django.conf import settings
from django.contrib.sites.models import Site

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

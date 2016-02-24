from urllib2 import HTTPError
import random

from django.conf import settings
from django.contrib.gis.geos import Point

from factory.fuzzy import BaseFuzzyAttribute
from sodapy import Socrata


def validate_license(license_number, full_name):
    if settings.DEBUG:
        return True
    else:
        client = Socrata(settings.TLC_URL, settings.APP_TOKEN)
        try:
            resp = client.get(settings.TLC_OPEN_DATA_ID,
                              license_number=license_number, name=full_name)
        except HTTPError:
            return False
        else:
            return len(resp) > 0


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-90.0, -90.0),
                     random.uniform(-100.0, -100.0))

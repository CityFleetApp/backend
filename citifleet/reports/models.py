from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _


class Report(models.Model):
    '''
    Stores report's type, location and last update time
    '''
    POLICE = 1
    TLC = 2
    ACCIDENT = 3
    TRAFFIC_JAM = 4
    HAZARD = 5
    ROAD_CLOSURE = 6

    REPORT_CHOICES = (
        (POLICE, _('Police')),
        (TLC, _('TLC')),
        (ACCIDENT, _('Accident')),
        (TRAFFIC_JAM, _('Traffic Jam')),
        (HAZARD, _('Hazard')),
        (ROAD_CLOSURE, _('Road Closure')),
    )

    location = models.PointField(_('location'))
    report_type = models.PositiveSmallIntegerField(_('type'), choices=REPORT_CHOICES)
    updated = models.DateTimeField(_('updated'), auto_now=True)

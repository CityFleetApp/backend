import random

from django.contrib.gis.geos import Point

from factory.fuzzy import BaseFuzzyAttribute
from factory import DjangoModelFactory

from .models import Report


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),
                     random.uniform(-90.0, 90.0))


class ReportFactory(DjangoModelFactory):
    location = FuzzyPoint()
    report_type = Report.POLICE

    class Meta:
        model = Report

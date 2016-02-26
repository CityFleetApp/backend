import random

from factory.fuzzy import BaseFuzzyAttribute

from django.contrib.gis.geos import Point


class FuzzyPoint(BaseFuzzyAttribute):
    '''
    Generates random location for factories in tests
    '''
    def fuzz(self):
        return Point(random.uniform(-90.0, -90.0),
                     random.uniform(-100.0, -100.0))

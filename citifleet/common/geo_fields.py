# -*- coding: utf-8 -*-

import json
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.error import GEOSException
from django.utils.encoding import smart_str
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

EMPTY_VALUES = (None, '', [], (), {})


class PointField(serializers.Field):
    type_name = 'PointField'
    type_label = 'point'

    default_error_messages = {
        'invalid': _('Enter a valid location.'),
    }

    def to_internal_value(self, value):
        """
        Parse json data and return a point object
        """
        if value in EMPTY_VALUES and not self.required:
            return None

        if isinstance(value, six.string_types):
            try:
                value = value.replace("'", '"')
                value = json.loads(value)
            except ValueError:
                self.fail('invalid')

        if value and isinstance(value, dict):
            try:
                latitude = value.get("latitude")
                longitude = value.get("longitude")
                return GEOSGeometry('POINT(%(latitude)s %(longitude)s)' % {
                    "longitude": longitude,
                    "latitude": latitude}
                )
            except (GEOSException, ValueError):
                self.fail('invalid')
        self.fail('invalid')

    def to_representation(self, value):
        """
        Transform POINT object to json.
        """
        if value is None:
            return value

        if isinstance(value, GEOSGeometry):
            value = {
                "latitude": smart_str(value.x),
                "longitude": smart_str(value.y)
            }
        return value

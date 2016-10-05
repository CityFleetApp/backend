# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from rest_framework import serializers

from citifleet.reports.models import Report

User = get_user_model()


class LocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()

    def validate(self, attrs):
        attrs['location'] = Point(attrs['lat'], attrs['lng'])
        return attrs


class ReportSerializer(serializers.ModelSerializer):
    """ Reports Model serializer. Serializes lat and lng to report's location """
    lat = serializers.FloatField(source='location.x')
    lng = serializers.FloatField(source='location.y')

    class Meta:
        model = Report
        fields = ('report_type', 'lat', 'lng', 'id')

    def validate(self, attrs):
        attrs['location'] = Point(attrs['location']['x'], attrs['location']['y'])
        return attrs

    def create(self, validated_data):
        instance = super(ReportSerializer, self).create(validated_data)
        instance.user.notified_reports.add(instance)
        for u in User.objects.filter(location__isnull=False).exclude(pk=instance.user.pk):
            u.notified_reports.add(instance)

        return instance

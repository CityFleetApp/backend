from django.contrib.gis.geos import Point

from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source='location.x')
    lng = serializers.FloatField(source='location.y')

    class Meta:
        model = Report
        fields = ('report_type', 'lat', 'lng')

    def validate(self, attrs):
        attrs['location'] = Point(attrs['location']['x'], attrs['location']['y'])
        return attrs

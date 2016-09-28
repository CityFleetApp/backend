from django.contrib.gis.geos import Point

from rest_framework import serializers

from .models import Report


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

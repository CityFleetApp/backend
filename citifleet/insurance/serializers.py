from rest_framework import serializers

from .models import InsuranceBroker


class InsuranceBrokerSerializer(serializers.ModelSerializer):

    class Meta:
        model = InsuranceBroker
        fields = ('name', 'years_of_experience', 'rating', 'phone', 'address')


class UploadFileSerializer(serializers.Serializer):
    document = serializers.FileField()
    broker = serializers.InsuranceBroker()

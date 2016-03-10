from rest_framework import serializers

from .models import Benefit


class BenefitSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('image_thumbnail', 'name', 'barcode')
        model = Benefit

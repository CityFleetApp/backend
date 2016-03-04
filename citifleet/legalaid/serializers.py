from rest_framework import serializers

from .models import InsuranceBroker, Accounting


class LegalAidBaseSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'years_of_experience', 'rating', 'phone', 'address')


class InsuranceBrokerSerializer(serializers.ModelSerializer):

    class Meta(LegalAidBaseSerializer.Meta):
        model = InsuranceBroker


class AccountingSerializer(serializers.ModelSerializer):

    class Meta(LegalAidBaseSerializer.Meta):
        model = Accounting

from rest_framework import serializers

from .models import InsuranceBroker, Accounting, DMVLawyer, TLCLawyer


class LegalAidBaseSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'years_of_experience', 'rating', 'phone', 'address')


class InsuranceBrokerSerializer(serializers.ModelSerializer):

    class Meta(LegalAidBaseSerializer.Meta):
        model = InsuranceBroker


class AccountingSerializer(serializers.ModelSerializer):

    class Meta(LegalAidBaseSerializer.Meta):
        model = Accounting


class DMVLawyerSerializer(serializers.ModelSerializer):

    class Meta(LegalAidBaseSerializer.Meta):
        model = DMVLawyer


class TLCLawyerSerializer(serializers.ModelSerializer):

    class Meta(LegalAidBaseSerializer.Meta):
        model = TLCLawyer

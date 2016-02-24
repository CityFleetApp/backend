from rest_framework import serializers

from .models import Accounting


class AccountingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Accounting
        fields = ('name', 'years_of_experience', 'rating', 'phone', 'address')

from django.utils.translation import ugettext as _

from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ('file', 'expiry_date', 'plate_number', 'document_type')

    def validate(self, attrs):
        if attrs['document_type'] == Document.TLC_PLATE_NUMBER and not attrs['plate_number']:
            raise serializers.ValidationError(_('Plate number can not be blank'))
        elif attrs['document_type'] != Document.TLC_PLATE_NUMBER and not attrs['expiry_date']:
            raise serializers.ValidationError(_('Epxiry date can not be blank'))

        return attrs

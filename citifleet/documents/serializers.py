from django.utils.translation import ugettext as _
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse

from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    '''
    Serializer for retrieving and uploading documents
    '''
    class Meta:
        model = Document
        fields = ('id', 'file', 'expiry_date', 'plate_number', 'document_type', 'expired')

    def validate(self, attrs):
        '''
        Check that tlc plate number is not empty for tlc plate document
        Check that expiry_date is not empty for all documents except tlc plate document
        '''
        if attrs.get('document_type'):
            if attrs['document_type'] == Document.TLC_PLATE_NUMBER and not attrs['plate_number']:
                raise serializers.ValidationError(_('Plate number can not be blank'))
            elif attrs['document_type'] != Document.TLC_PLATE_NUMBER and not attrs['expiry_date']:
                raise serializers.ValidationError(_('Epxiry date can not be blank'))

        attrs['user'] = self.context['request'].user
        return attrs

    def save(self, **kwargs):
        instance = super(DocumentSerializer, self).save(**kwargs)
        instance.status = Document.UNDER_REVIEW
        instance.save()

        mail_admins(
            _('Document requires verification'),
            _('Verity the document using the link {}').format(
                reverse('admin:documents_document_change', args=[instance.id])))

        return instance

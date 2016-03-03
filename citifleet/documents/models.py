from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Document(models.Model):
    DMV_LICENSE = 1
    HACK_LICENSE = 2
    INSURANCE = 3
    DIAMOND_CARD = 4
    INSURANCE_CERTIFICATE = 5
    LIABILITY_CERTIFICATE = 6
    TLC_PLATE_NUMBER = 7
    DRUG_TEST = 8

    DOCUMENT_TYPES = (
        (DMV_LICENSE, _('DMV License')),
        (HACK_LICENSE, _('Hack License')),
        (INSURANCE, _('Insurance')),
        (DIAMOND_CARD, _('Diamond Card')),
        (INSURANCE_CERTIFICATE, _('Insurance Certificate')),
        (LIABILITY_CERTIFICATE, _('Certificate Of Liability')),
        (TLC_PLATE_NUMBER, _('TLC Plate Number')),
        (DRUG_TEST, _('Drug Test')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))
    file = models.FileField(_('document'), upload_to='documents/')
    expiry_date = models.DateField(_('expiry date'), null=True)
    document_type = models.PositiveSmallIntegerField(_('document type'), choices=DOCUMENT_TYPES)
    plate_number = models.CharField(_('tlc plate number'), max_length=100, blank=True)

    class Meta:
        unique_together = ('user', 'document_type')

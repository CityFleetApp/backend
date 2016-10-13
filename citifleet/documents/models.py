# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Document(models.Model):
    """
    Store document info that driver can upload from app
    Unique together index prevent from creating several documents of the same type for one driver
    """

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

    UNDER_REVIEW = 1
    DECLINED = 2
    CONFIRMED = 3

    STATUS_CHOICES = (
        (UNDER_REVIEW, _('Under Review')),
        (DECLINED, _('Declined')),
        (CONFIRMED, _('Confirmed')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name='documents')
    file = models.FileField(_('document'), upload_to='documents/')
    expiry_date = models.DateField(_('expiry date'), null=True, blank=True)
    document_type = models.PositiveSmallIntegerField(_('document type'), choices=DOCUMENT_TYPES)
    plate_number = models.CharField(_('tlc plate number'), max_length=100, blank=True)
    status = models.PositiveSmallIntegerField(_('status'), choices=STATUS_CHOICES, default=UNDER_REVIEW)

    class Meta:
        unique_together = ('user', 'document_type')
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def expired(self):
        return self.document_type != Document.TLC_PLATE_NUMBER and self.expiry_date < timezone.now().date()
    expired.boolean = True

    def get_type_repr(self):
        return dict(Document.DOCUMENT_TYPES)[self.document_type]

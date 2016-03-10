from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


class LegalAidBase(models.Model):
    '''
    Base class for models in Legal Aid section
    '''
    name = models.CharField(_('name'), max_length=200)
    years_of_experience = models.IntegerField(_('years of experience'))
    rating = models.PositiveSmallIntegerField(_('rating'), choices=zip(range(6), range(6)))
    phone = PhoneNumberField(_('phone'))
    address = models.CharField(_('address'), max_length=250)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '{}, {}'.format(self.name, self.phone)


class Accounting(LegalAidBase):
    '''
    Store Accounting data. Filled via admin interface.
    '''
    class Meta:
        verbose_name = _('Accounting')
        verbose_name_plural = _('Accounting')


class InsuranceBroker(LegalAidBase):
    '''
    Store insurance broker info. Filled via admin interface.
    '''
    class Meta:
        verbose_name = _('Insurance Broker')
        verbose_name_plural = _('Insurance Brokers')


class DMVLawyer(LegalAidBase):
    '''
    Store DMV lawyer info
    '''
    class Meta:
        verbose_name = _('DMV Lawyer')
        verbose_name_plural = _('DMV Lawyers')


class TLCLawyer(LegalAidBase):
    '''
    Store TLC lawyer info
    '''
    class Meta:
        verbose_name = _('TLC Lawyer')
        verbose_name_plural = _('TLC Lawyers')

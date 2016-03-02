from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class InsuranceBroker(models.Model):
    '''
    Store insurance broker info. Filled via admin interface.
    Phone format - international (+41524204242)
    '''
    name = models.CharField(_('name'), max_length=200)
    years_of_experience = models.IntegerField(_('years of experience'))
    rating = models.PositiveSmallIntegerField(_('rating'))
    phone = PhoneNumberField(_('phone'))
    address = models.CharField(_('address'), max_length=250)

    class Meta:
        verbose_name = _('Insurance Broker')
        verbose_name_plural = _('Insurance Brokers')

    def __unicode__(self):
        return '{}, {}'.foramt(self.name, self.phone)

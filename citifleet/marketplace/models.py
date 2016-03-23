from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from citifleet.users.models import User


class CarMake(models.Model):
    name = models.CharField(_('Name'), max_length=150)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Car Make')
        verbose_name_plural = _('Car Makes')


class CarModel(models.Model):
    name = models.CharField(_('Name'), max_length=150)
    make = models.ForeignKey(CarMake, verbose_name=_('Make'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Car Model')
        verbose_name_plural = _('Car Models')


class Car(models.Model):
    E85 = 1
    REGULAR_87 = 2
    PLUS89 = 3
    PREMIUM9193 = 4
    DIESEL = 5
    ELECTRIC = 6

    FUEL_TYPES = (
        (E85, _('E85')),
        (REGULAR_87, _('87 Regular')),
        (PLUS89, _('89 Plus')),
        (PREMIUM9193, _('91-93 Premium')),
        (DIESEL, _('Diesel')),
        (ELECTRIC, _('Electric')),
    )

    UBERX = 1
    UBERXL = 2
    BLACK = 3
    SUV = 4
    LUX = 5

    TYPES = (
        (UBERX, _('UberX/Lyft')),
        (UBERXL, _('UberXL/LyftPlus')),
        (BLACK, _('Black')),
        (SUV, _('SUV')),
        (LUX, _('LUX')),
    )

    make = models.ForeignKey(CarMake, verbose_name=_('Make'))
    model = models.ForeignKey(CarModel, verbose_name=_('Model'))
    type = models.PositiveSmallIntegerField(_('Type'), choices=TYPES)
    color = models.CharField(_('Color'), max_length=50)
    year = models.IntegerField(_('Year'))
    fuel = models.PositiveSmallIntegerField(_('Fuel'), choices=FUEL_TYPES)
    seats = models.PositiveSmallIntegerField(_('Seats'), choices=[(i, i) for i in range(4, 9)])
    price = models.DecimalField(_('Price'), max_digits=7, decimal_places=2)
    description = models.TextField(_('Description'))
    rent = models.BooleanField(_('For rent'), default=False)
    owner = models.ForeignKey(User, verbose_name=_('Owner'))

    def __unicode__(self):
        return '{}{}'.format(self.make, self.model)

    class Meta:
        verbose_name = _('Car')
        verbose_name_plural = _('Cars')

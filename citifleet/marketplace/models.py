from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from citifleet.users.models import User
from citifleet.common.utils import get_full_path


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

    BLACK = 1
    WHITE = 2
    RED = 3

    COLORS = (
        (BLACK, _('Black')),
        (WHITE, _('White')),
        (RED, _('Red')),
    )

    make = models.ForeignKey(CarMake, verbose_name=_('Make'))
    model = models.ForeignKey(CarModel, verbose_name=_('Model'))
    type = models.PositiveSmallIntegerField(_('Type'), choices=TYPES)
    color = models.PositiveSmallIntegerField(_('Color'), choices=COLORS)
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


class CarPhoto(models.Model):
    car = models.ForeignKey(Car, verbose_name=_('Car'), related_name='photos')
    file = models.ImageField(_('Photo'), upload_to='cars/')

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def __unicode__(self):
        return get_full_path(self.file.url)


class GeneralGood(models.Model):
    BRAND_NEW = 1
    NEW = 2
    USED_GOOD = 3
    USED = 4

    CONDITION_CHOICES = (
        (BRAND_NEW, _('Brand New (Never Used)')),
        (NEW, _('New (Slightly Used)')),
        (USED_GOOD, _('Used (Good Condition)')),
        (USED, _('Used'))
    )

    item = models.CharField(_('Item'), max_length=250)
    price = models.DecimalField(_('Price'), max_digits=6, decimal_places=2)
    condition = models.SmallIntegerField(_('Condition'), choices=CONDITION_CHOICES)
    description = models.CharField(_('Description'), max_length=250)
    owner = models.ForeignKey(User, verbose_name=_('User'))


class GoodPhoto(models.Model):
    goods = models.ForeignKey(GeneralGood, verbose_name=_('Good'), related_name='photos')
    file = models.ImageField(_('Photo'), upload_to='goods/')

    class Meta:
        verbose_name = _('General Goods Photo')
        verbose_name_plural = _('General Goods Photos')

    def __unicode__(self):
        return get_full_path(self.file.url)


class JobOffer(models.Model):
    REGULAR = 1
    BLACK = 2
    SUV = 3
    LUX = 4

    VEHICLE_CHOICES = (
        (REGULAR, _('Regular')),
        (BLACK, _('Black')),
        (SUV, _('SUV')),
        (LUX, _('LUX'))
    )

    DROP_OFF = 1
    WAIT_AND_RETURN = 2
    HOURLY = 3

    JOB_CHOICES = (
        (DROP_OFF, _('Drop off')),
        (WAIT_AND_RETURN, _('Wait & Return')),
        (HOURLY, _('Hourly')),
    )

    pickup_datetime = models.DateTimeField(_('Pickup datetime'))
    pickup_address = models.CharField(_('Pickup address'), max_length=255)
    destination = models.CharField(_('Destination'), max_length=255)
    fare = models.DecimalField(_('Fare'), max_digits=5, decimal_places=2)
    gratuity = models.DecimalField(_('Gratuity'), max_digits=5, decimal_places=2)
    vehicle_type = models.PositiveSmallIntegerField(_('Vehicle Type'), choices=VEHICLE_CHOICES)
    suite = models.BooleanField(_('Suite/Tie'), default=False)
    job_type = models.PositiveSmallIntegerField(_('Job Type'), choices=JOB_CHOICES)
    instructions = models.CharField(_('Instructions'), max_length=255)
    company = models.ForeignKey(User, related_name='offers', null=True, blank=True)
    owner = models.ForeignKey(User, related_name='job_postings')

    class Meta:
        verbose_name = _('Job Offer')
        verbose_name_plural = _('Job Offers')

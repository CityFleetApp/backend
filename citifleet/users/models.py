# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from phonenumber_field.modelfields import PhoneNumberField

from citifleet.common.utils import get_protocol


class UserManager(BaseUserManager):

    def create_user(self, **kwargs):
        user = User(**kwargs)
        user.set_password(kwargs['password'])
        user.save()
        return user

    def create_superuser(self, email, password):
        return self.create_user(email=email, password=password, phone='1', hack_license='1',
                                full_name='admin', is_staff=True, is_superuser=True)


@python_2_unicode_compatible
class User(AbstractUser):
    '''
    Custom user model.
    phone and email fields - unique
    location is saved using data from mobile app
    hack_license is verified via SODA API
    phone format - international (+41524204242)
    '''
    phone = PhoneNumberField(_('phone'))
    hack_license = models.CharField(_('hack license'), max_length=150)
    full_name = models.CharField(_('full name'), max_length=200)
    location = models.PointField(_('location'), null=True, blank=True)
    bio = models.TextField(_('bio'), blank=True)
    drives = models.CharField(_('drives'), max_length=200, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def avatar_url(self):
        '''
        Return full avatar url
        '''
        if self.avatar:
            return '{}{}{}'.format(get_protocol(), Site.objects.get_current().domain, self.avatar.url)
        else:
            return ''

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    AbstractUser._meta.get_field('email')._unique = True

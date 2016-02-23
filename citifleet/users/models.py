# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):

    def create_user(self, **kwargs):
        user = User(**kwargs)
        user.set_password(kwargs['password'])
        user.save()
        return user


@python_2_unicode_compatible
class User(AbstractUser):
    phone = PhoneNumberField(_('phone'))
    hack_license = models.CharField(_('hack license'), max_length=150)
    full_name = models.CharField(_('full name'), max_length=200)
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    AbstractUser._meta.get_field('email')._unique = True

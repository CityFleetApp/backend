# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class User(AbstractUser):
    phone = models.CharField(_('phone'), max_length=50)
    hack_license = models.CharField(_('hack license'), max_length=150)
    full_name = models.CharField(_('full name'), max_length=200)

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    AbstractUser._meta.get_field('email')._unique = True

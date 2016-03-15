# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField
from easy_thumbnails.files import get_thumbnailer

from citifleet.documents.models import Document
from citifleet.common.utils import get_full_path


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
    friends = models.ManyToManyField("self", null=True)

    facebook_id = models.CharField(_('facebook id'), max_length=200, blank=True)
    twitter_id = models.CharField(_('twitter id'), max_length=200, blank=True)
    instagram_id = models.CharField(_('instagram id'), max_length=200, blank=True)

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
            return get_full_path(self.avatar.url)
        else:
            return ''

    @property
    def documents_up_to_date(self):
        return self.documents.filter(status=Document.CONFIRMED,
                                     expiry_date__isnull=False, expiry_date__gt=timezone.now().date()).exists()

    @property
    def jobs_completed(self):
        # Returns dummy result till jobs section is done
        return 12

    @property
    def rating(self):
        # Returns dummy result till jobs section is done
        return 4

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    AbstractUser._meta.get_field('email')._unique = True


class Photo(models.Model):
    '''
    Store uploaded user's photos
    '''
    file = models.ImageField(_('photo'), upload_to='photos/')
    user = models.ForeignKey(User, verbose_name=_('user'))
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    @property
    def thumbnail(self):
        '''
        Return photo's thumbnail url
        '''
        return get_full_path(get_thumbnailer(self.file).get_thumbnail({
            'size': (250, 250),
            'crop': True,
            'detail': True,
        }).url)

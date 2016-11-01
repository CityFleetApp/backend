# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from model_utils.choices import Choices
from model_utils.models import TimeStampedModel

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.templatetags.static import static
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import Avg

from easy_thumbnails.files import get_thumbnailer

from citifleet.documents.models import Document
from citifleet.common.utils import get_full_path
from citifleet.marketplace.models import Car, JobOffer
from citifleet.users.signals import user_location_changed
from citifleet.common.utils import generate_username


class UserManager(BaseUserManager):

    def create_user(self, **kwargs):
        user = User(**kwargs)
        if not user.username:
            user.username = generate_username(kwargs.get('full_name', '')) or user.email
        user.set_password(kwargs['password'])
        user.save()
        return user

    def create_superuser(self, email, password):
        return self.create_user(email=email, password=password, phone='1', hack_license='1',
                                full_name='admin', is_staff=True, is_superuser=True,
                                user_type=User.USER_TYPES.staff)


class AllowNotificationManager(UserManager):

    def get_queryset(self):
        return super(UserManager, self).get_queryset().filter(notifications_enabled=True)


@python_2_unicode_compatible
class User(AbstractUser):
    """
    Custom user model.
    phone and email fields - unique
    location is saved using data from mobile app
    hack_license is verified via SODA API
    phone format - international (+41524204242)
    """
    USER_TYPES = Choices(
        (0, 'user', 'Just a User'),
        (1, 'staff', 'Any staff user (admin/superuser/staff)')
    )

    phone = models.CharField(_('phone'), max_length=12)
    hack_license = models.CharField(_('hack license'), max_length=150, blank=True)
    full_name = models.CharField(_('full name'), max_length=200)
    location = models.PointField(_('location'), null=True, blank=True)
    datetime_location_changed = models.DateTimeField(_('time location changed'), blank=True, null=True)
    bio = models.TextField(_('bio'), blank=True)
    drives = models.CharField(_('drives'), max_length=200, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)
    friends = models.ManyToManyField("self", null=True)

    facebook_id = models.CharField(_('facebook id'), max_length=200, blank=True)
    google_id = models.CharField(_('google id'), max_length=200, blank=True)
    twitter_id = models.CharField(_('twitter id'), max_length=200, blank=True)
    instagram_id = models.CharField(_('instagram id'), max_length=200, blank=True)

    notifications_enabled = models.BooleanField(_('notifications enabled'), default=True)
    chat_privacy = models.BooleanField(_('chat privacy'), default=True)
    visible = models.BooleanField(_('visible'), default=True)

    car_make = models.ForeignKey('marketplace.CarMake', null=True, blank=True)
    car_model = models.ForeignKey('marketplace.CarModel', null=True, blank=True)
    car_year = models.PositiveIntegerField(_('Car year'), null=True, blank=True)
    car_type = models.PositiveIntegerField(_('Car type'), null=True, choices=Car.TYPES, blank=True)
    car_color = models.PositiveIntegerField(_('Car color'), null=True, choices=Car.COLORS, blank=True)

    notified_reports = models.ManyToManyField('reports.Report', blank=True, related_name='notified_users')
    user_type = models.SmallIntegerField(_('user type'), choices=USER_TYPES, default=USER_TYPES.user)

    objects = UserManager()
    with_notifications = AllowNotificationManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def avatar_url(self):
        """ Return full avatar url """
        picture_url = static('images/default_profile_picture.png')
        if self.avatar:
            picture_url = self.avatar.url
        return get_full_path(picture_url)

    def set_location(self, new_location, in_background=False, commit=True):
        self.location = new_location
        if not in_background:
            self.datetime_location_changed = timezone.now()

        if commit:
            self.save()

        user_location_changed.send(sender=self.__class__, user=self)
        return self

    @property
    def drives(self):
        if self.car_make and self.car_model:
            return '{}/{}'.format(self.car_make.name, self.car_model.name)
        return ''

    @property
    def documents_up_to_date(self):
        return self.documents.filter(status=Document.CONFIRMED,
                                     expiry_date__isnull=False, expiry_date__gt=timezone.now().date()).exists()

    @property
    def jobs_completed(self):
        return JobOffer.objects.filter(status=JobOffer.COMPLETED, driver=self).count()

    @property
    def rating(self):
        return JobOffer.objects.filter(status=JobOffer.COMPLETED, driver=self).aggregate(
            rating=Avg('driver_rating'))['rating'] or 5.0

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    AbstractUser._meta.get_field('email')._unique = True


class Photo(models.Model):
    """ Store uploaded user's photos """
    file = models.ImageField(_('photo'), upload_to='photos/')
    user = models.ForeignKey(User, verbose_name=_('user'))
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    @property
    def thumbnail(self):
        """ Return photo's thumbnail url """
        return get_full_path(get_thumbnailer(self.file).get_thumbnail({
            'size': (255, 255),
            'crop': True,
            'detail': True,
        }).url)


class FriendRequest(TimeStampedModel):
    error_messages = {
        'duplicate_error': _('You have already invited user to become your friend'),
        'user_is_already_friend_error': _('You have already had this user in you friends'),
        'user_try_to_invite_himself_error': _('You can\'t invite yourself to become a friend'),
    }

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('From User'),
        related_name='outgoing_friend_requests',
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('To User'),
        related_name='incoming_friend_requests',
    )

    def __str__(self):
        return 'Friend request from %s to %s' % (self.from_user, self.to_user)

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError(self.error_messages['user_try_to_invite_himself_error'])
        if self.from_user.friends.filter(pk=self.to_user.pk).exists():
            raise ValidationError(self.error_messages['user_is_already_friend_error'])

        already_exitst_qs = FriendRequest.objects.filter(from_user=self.from_user, to_user=self.to_user)
        if self.pk and already_exitst_qs.exclude(pk=self.pk).exists() or not self.pk and already_exitst_qs.exists():
            raise ValidationError(self.error_messages['duplicate_error'])

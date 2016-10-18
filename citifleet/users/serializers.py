# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

import requests
from oauth2client import client, crypt

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

import tweepy
from instagram.client import InstagramAPI
from open_facebook import OpenFacebook
from rest_framework import serializers

from citifleet.common.utils import validate_username
from citifleet.common.geo_fields import PointField
from citifleet.users.models import Photo, FriendRequest
from citifleet.users.mixins import (RegistrationSerializerMixin, SocialAuthSerializerMixin,
                                    SocialCreateSerializerMixin)

User = get_user_model()


class SignupSerializer(RegistrationSerializerMixin, serializers.ModelSerializer):
    """ Serializes sign up data. Creates new user and login him automatically """
    password_confirm = serializers.CharField(max_length=128)

    class Meta(RegistrationSerializerMixin.Meta):
        fields = RegistrationSerializerMixin.Meta.fields + ('password', 'password_confirm')

    def validate(self, attrs):
        if attrs.get('password') and attrs.get('password_confirm'):
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError(_('Passwords don\'t match'))
            del attrs['password_confirm']
        return super(SignupSerializer, self).validate(attrs)


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializes email and provides method to reset password for user
    with passed email
    """
    email = serializers.EmailField()

    def validate(self, attrs):
        """ Checks if user with passed email exists in database """
        try:
            self.user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address")

        return attrs

    def reset_password(self):
        """ Generate and set new password. Send email with new password """
        new_password = User.objects.make_random_password(length=10)
        self.user.set_password(new_password)
        self.user.save()

        send_mail('Password reset', 'Your new password is {}'.format(new_password),
                  settings.DEFAULT_FROM_EMAIL, [self.user.email])


class ChangePasswordSerializer(serializers.Serializer):
    """ Serialize new password's length and provide method to change password """
    old_password = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)
    password_confirm = serializers.CharField(max_length=128)

    def validate_old_password(self, value):
        if not self.context['user'].check_password(value):
            raise serializers.ValidationError('Wrong password')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")

        del attrs['password_confirm']
        return attrs

    def change_password(self):
        """ Get user from serializer's context and change password """
        user = self.context['user']
        user.set_password(self.validated_data['password'])
        user.save()


class UserDetailSerializer(serializers.ModelSerializer):
    """ Serializer for user details screen """

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'hack_license', 'username',
                  'bio', 'drives', 'avatar_url', 'documents_up_to_date', 'jobs_completed',
                  'rating', 'id', 'user_type', )


class ContactsSerializer(serializers.Serializer):
    """ Take list of phone numbers and return list of users with these numbers """
    contacts = serializers.ListField(child=serializers.CharField())

    def validate(self, attrs):
        request_user = self.context['user']
        contacts = [re.sub(r'\+\d', '', c) for c in attrs['contacts']]
        attrs['users'] = User.objects.filter(phone__in=contacts).exclude(pk=request_user.pk)
        return attrs


class FacebookSerializer(serializers.Serializer):
    """
    Take facebook token and facebook id
    Fetch friends list from facebook
    """
    token = serializers.CharField()

    def validate(self, attrs):
        graph = OpenFacebook(attrs['token'])
        self_id = graph.get('me', fields='id')['id']
        friends_ids = graph.get('me/friends', fields='id')['data']
        attrs['users'] = User.objects.filter(facebook_id__in=[f['id'] for f in friends_ids])

        user = self.context['user']
        if not user.facebook_id:
            user.facebook_id = self_id
            user.save()
        return attrs


class TwitterSerializer(serializers.Serializer):
    """
    Take twitter token and secret token
    Fetch friends list from twitter
    """
    token = serializers.CharField()
    token_secret = serializers.CharField()

    def validate(self, attrs):
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(attrs['token'], attrs['token_secret'])
        api = tweepy.API(auth)

        me = api.me()
        friends_ids = api.friends_ids(me.id)
        attrs['users'] = User.objects.filter(twitter_id__in=friends_ids)

        user = self.context['user']
        if not user.twitter_id:
            user.twitter_id = me.id
            user.save()
        return attrs


class InstagramSerializer(serializers.Serializer):
    """
    Take instagram token
    Fetch friends list from instagram
    """
    token = serializers.CharField()

    def validate(self, attrs):
        api = InstagramAPI(access_token=attrs['token'], client_secret=settings.INSTAGRAM_CLIENT_SECRET)

        me = api.user()
        follows, next_ = api.user_follows()
        while next_:
            more_follows, next_ = api.user_follows(with_next_url=next_)
            follows.extend(more_follows)

        attrs['users'] = User.objects.filter(instagram_id__in=[f['id'] for f in follows])

        user = self.context['user']
        if not user.instagram_id:
            user.instagram_id = me.id
            user.save()
        return attrs


class AvatarSerializer(serializers.ModelSerializer):
    """ Update user avatar """
    class Meta:
        model = User
        fields = ('avatar',)


class PhotoSerializer(serializers.ModelSerializer):
    """ Serialize uploaded photo """
    class Meta:
        model = Photo
        fields = ('id', 'file', 'thumbnail')

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        return attrs


class SettingsSerializer(serializers.ModelSerializer):
    """ Serialize user's settings info """
    class Meta:
        model = User
        fields = ('notifications_enabled', 'chat_privacy', 'visible')


class ProfileSerializer(serializers.ModelSerializer):
    """ Serialize user personal info """
    car_make_display = serializers.ReadOnlyField(source='car_make.name')
    car_model_display = serializers.ReadOnlyField(source='car_model.name')
    car_color_display = serializers.ReadOnlyField(source='get_car_color_display')
    car_type_display = serializers.ReadOnlyField(source='get_car_type_display')

    class Meta:
        model = User
        fields = ('car_make', 'car_model', 'bio', 'username', 'car_year', 'car_type', 'phone',
                  'car_color', 'car_make_display', 'car_model_display', 'car_color_display', 'car_type_display')


class FriendSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source='location.x')
    lng = serializers.FloatField(source='location.y')

    class Meta:
        model = User
        fields = ('id', 'avatar_url', 'full_name', 'email', 'username', 'phone', 'lat', 'lng')


class UsernameInUseSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length=User._meta.get_field('username').max_length,
        allow_blank=True,
        required=False,
    )

    def validate_username(self, username):
        if username:
            username = validate_username(username)
        return username


class UpdateUserLocationSerializer(serializers.ModelSerializer):
    location = PointField()

    class Meta:
        model = User
        fields = ('location', )

    def save(self, **kwargs):
        return self.instance.set_location(self.validated_data['location'])


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'phone', 'id', 'email', 'avatar_url')


class FriendsFromContactsSerializer(serializers.Serializer):
    phones = serializers.ListField(child=serializers.CharField(), required=False)
    emails = serializers.ListField(child=serializers.EmailField(), required=False)

    def validate_phones(self, phones):
        return [re.sub(r'\D', '', phone) for phone in phones]

    def get_users(self, user):
        emails = self.validated_data.get('emails', [])
        phones = self.validated_data.get('phones', [])
        return User.objects.filter(
            models.Q(email__in=emails) |
            models.Q(phone__in=phones)
        ).exclude(models.Q(pk=user.pk) | models.Q(pk__in=user.friends.only('id').values_list('id', flat=True)))


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = SimpleUserSerializer()
    to_user = SimpleUserSerializer()

    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user')


class CreateFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'to_user')

    def validate(self, data):
        request = self.context.get('request')
        to_user = data.get('to_user')
        if to_user and request and request.user and request.user.is_authenticated():
            if request.user == data['to_user']:
                raise serializers.ValidationError(FriendRequest.error_messages['user_try_to_invite_himself_error'])
            if request.user.friends.filter(pk=data['to_user'].pk).exists():
                raise serializers.ValidationError(FriendRequest.error_messages['user_is_already_friend_error'])
            if FriendRequest.objects.filter(from_user=request.user, to_user=data['to_user']).exists():
                raise serializers.ValidationError(FriendRequest.error_messages['duplicate_error'])
        return data


class UserLoginSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='auth_token')

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'hack_license', 'username',
                  'bio', 'drives', 'avatar_url', 'documents_up_to_date',
                  'jobs_completed', 'rating', 'id', 'user_type', 'token', )


class SocialAuthFailedSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'full_name', 'username', )


class FacebookAuthSerializer(SocialAuthSerializerMixin, serializers.Serializer):
    ACCOUNT_TYPE = 'facebook'

    token = serializers.CharField(required=True, allow_blank=False)

    def validate_token(self, token):
        if token:
            social_account_url = 'https://graph.facebook.com/me/?fields=id,email,name,first_name,last_name&access_token=' + token  # noqa
            resp = requests.get(social_account_url)
            if resp.status_code != 200:
                raise serializers.ValidationError(_('Invalid access token'))
            self.social_response = resp.json()
        return token


class GoogleAuthSeriaizer(SocialAuthSerializerMixin, serializers.Serializer):
    ISS_LIST = ['accounts.google.com', 'https://accounts.google.com']
    ACCOUNT_TYPE = 'google'

    token = serializers.CharField(required=True, allow_blank=False)

    def validate_token(self, token):
        if token:
            try:
                client_ids = settings.GOOGLE_CLIENT_IDS
                response = client.verify_id_token(token, client_ids[0])
                if response.get('aud') and response['aud'] not in client_ids:
                    raise serializers.ValidationError(_('Invalid client'))
                if response.get('iss') and response['iss'] not in self.ISS_LIST:
                    raise serializers.ValidationError(_('Invalid issuer'))
                if response.get('hd') and response['hd'] != settings.GOOGLE_APPS_DOMAIN_NAME:
                    raise serializers.ValidationError(_('Invalid hosted domain'))
            except crypt.AppIdentityError:
                raise serializers.ValidationError(_('Invalid Token ID'))
            self.social_response = response
        return token


class FacebookSocialAccountCreateSerializer(SocialCreateSerializerMixin, FacebookAuthSerializer,
                                            serializers.ModelSerializer):
    token = serializers.CharField(required=True, allow_blank=False)

    class Meta(RegistrationSerializerMixin.Meta):
        fields = RegistrationSerializerMixin.Meta.fields + ('token', )


class GoogleSocialAccountCreateSerializer(SocialCreateSerializerMixin, GoogleAuthSeriaizer,
                                          serializers.ModelSerializer):
    token = serializers.CharField(required=True, allow_blank=False)

    class Meta(RegistrationSerializerMixin.Meta):
        fields = RegistrationSerializerMixin.Meta.fields + ('token', )

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from citifleet.common.utils import generate_username, validate_username

User = get_user_model()


class RegistrationSerializerMixin(object):
    username = serializers.CharField(
        max_length=User._meta.get_field('username').max_length,
        allow_blank=True,
        required=False,
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'blank': _('Email field can not be blank'),
            'required': _('Email field can not be blank'),
        }
    )

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone', 'username', )

    def validate_username(self, username):
        if username:
            username = validate_username(username)
        return username

    def validate_phone(self, value):
        try:
            int(value)
        except ValueError:
            raise serializers.ValidationError(_('The phone number entered is not valid.'))
        else:
            if len(value) != 10:
                raise serializers.ValidationError(_('The phone number entered is not valid.'))
            else:
                return value

    def validate_email(self, email):
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(_('This email is already in use.'))
        return email

    def validate(self, attrs):
        if not attrs.get('username'):
            attrs['username'] = generate_username(attrs.get('full_name', ''))
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        Token.objects.create(user=user)
        return user


class SocialAuthSerializerMixin(object):
    ACCOUNT_TYPE = None

    def __init__(self, *args, **kwargs):
        super(SocialAuthSerializerMixin, self).__init__(*args, **kwargs)
        self.social_response = None

    def social_account_in_use(self):
        if self.ACCOUNT_TYPE == 'facebook':
            return User.objects.filter(facebook_id=self.social_response['id']).exists()
        elif self.ACCOUNT_TYPE == 'google':
            return User.objects.filter(google_id=self.social_response['sub']).exists()
        return False

    def match_user(self):
        if self.ACCOUNT_TYPE == 'facebook' and self.social_account_in_use():
            return User.objects.get(facebook_id=self.social_response['id'])

        elif self.ACCOUNT_TYPE == 'google' and self.social_account_in_use():
            return User.objects.get(google_id=self.social_response['sub'])

        if self.social_response.get('email') and User.objects.filter(email=self.social_response['email']).exists():
            return User.objects.get(email=self.social_response['email'])

    def _get_user_data(self):
        social_response = self.social_response
        data = {
            'username': generate_username(social_response['name']),
            'full_name': social_response['name'],
        }
        if social_response.get('email'):
            data['email'] = social_response['email']
        return data

    def authenticate(self):
        user = self.match_user()
        user_data = self._get_user_data()
        if user:
            if self.ACCOUNT_TYPE == 'facebook':
                user.facebook_id = self.social_response['id']
            elif self.ACCOUNT_TYPE == 'google':
                user.google_id = self.social_response['sub']
            user.save()
            return user
        return User(**user_data)

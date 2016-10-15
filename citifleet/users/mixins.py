# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests

from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from citifleet.common.utils import generate_username

User = get_user_model()


class SocialSerializerMixin(object):
    social_account_endpoints = {
        'facebook': 'https://graph.facebook.com/me/?fields=id,email,name,first_name,last_name',
        'google': 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json',
    }
    social_account_type = None

    def _get_social_account_type(self):
        if not self.social_account_type:
            self.social_account_type = self.context['social_account']
        return self.social_account_type

    def _get_url(self, access_token):
        if access_token:
            social_account_url = self.social_account_endpoints.get(self._get_social_account_type())
            if social_account_url:
                return social_account_url + '&access_token=' + access_token
            return social_account_url

    def _get_user_data(self, social_response):
        data = {
            'username': generate_username(social_response['name']),
            'full_name': social_response['name'],
        }
        if social_response.get('email'):
            data['email'] = social_response['email']
        return data

    def match_user(self, social_response):
        kwargs = {}
        if self._get_social_account_type() == 'facebook':
            kwargs['facebook_id'] = social_response['id']
        elif self._get_social_account_type() == 'google':
            kwargs['google_id'] = social_response['id']

        if User.objects.filter(**kwargs).exists():
            return User.objects.get(**kwargs)

        if social_response.get('email') and User.objects.filter(email=social_response['email']).exists():
            return User.objects.get(email=social_response['email'])

    def update_user_social_id(self, user, social_response, commit=True):
        if self._get_social_account_type() == 'facebook':
            user.facebook_id = social_response['id']
        elif self._get_social_account_type() == 'google':
            user.google_id = social_response['id']

        if commit:
            user.save()
        return user

    def validate(self, attrs):
        social_account_url = self._get_url(attrs.get('access_token'))
        if social_account_url:
            resp = requests.get(social_account_url)
            if resp.status_code == 200:
                attrs['social_response'] = resp.json()
                return attrs
            raise serializers.ValidationError(_('Invalid access token'))
        raise serializers.ValidationError(_('Invalid social account type'))

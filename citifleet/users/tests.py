from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import User


@override_settings(DEBUG=True)
class TestSignup(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_signup_successful(self):
        signup_data = {
            'full_name': 'John Smith', 'email': 'john@example.com', 'username': 'johnsmith12',
            'phone': '+41524204242', 'hack_license': '123456', 'password': 'password',
            'password_confirm': 'password'
        }

        resp = self.client.post(reverse('users:signup'), data=signup_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)

    def test_signup_unsuccessful(self):
        signup_data = {
            'email': 'john@example.com', 'username': 'johnsmith12',
            'phone': '+41524204242', 'hack_license': '123456', 'password': 'password',
            'password_confirm': 'password'
        }

        resp = self.client.post(reverse('users:signup'), data=signup_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(resp.data, {'full_name': ['This field is required.']})

    def test_login_after_signup_successful(self):
        signup_data = {
            'full_name': 'John Smith', 'email': 'john@example.com', 'username': 'johnsmith12',
            'phone': '+41524204242', 'hack_license': '123456', 'password': 'password',
            'password_confirm': 'password'
        }
        resp = self.client.post(reverse('users:signup'), data=signup_data)
        token = Token.objects.get(user__email='john@example.com')

        login_data = {'username': 'john@example.com', 'password': 'password'}
        resp = self.client.post(reverse('users:login'), data=login_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {'token': token.key})

    def test_unique_email(self):
        signup_data = {
            'full_name': 'John Smith', 'email': 'john@example.com', 'username': 'johnsmith12',
            'phone': '+41524204242', 'hack_license': '123456', 'password': 'password',
            'password_confirm': 'password'
        }
        self.client.post(reverse('users:signup'), data=signup_data)

        signup_data['username'] = 'johnsmith13'
        resp = self.client.post(reverse('users:signup'), data=signup_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {'email': ['User with this email address already exists.']})

    def test_unique_username(self):
        signup_data = {
            'full_name': 'John Smith', 'email': 'john@example.com', 'username': 'johnsmith12',
            'phone': '+41524204242', 'hack_license': '123456', 'password': 'password',
            'password_confirm': 'password'
        }
        self.client.post(reverse('users:signup'), data=signup_data)

        signup_data['email'] = 'john12@example.com'
        resp = self.client.post(reverse('users:signup'), data=signup_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {'username': ['A user with that username already exists.']})

    def test_password_dont_match(self):
        signup_data = {
            'full_name': 'John Smith', 'email': 'john@example.com', 'username': 'johnsmith12',
            'phone': '+41524204242', 'hack_license': '123456', 'password': 'password',
            'password_confirm': 'password1'
        }

        resp = self.client.post(reverse('users:signup'), data=signup_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data, {'non_field_errors': ["Passwords don't match"]})

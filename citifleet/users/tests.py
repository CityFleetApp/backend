from tempfile import NamedTemporaryFile

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.core import mail

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from mock import patch
from PIL import Image

from .models import User
from .factories import UserFactory


@override_settings(DEBUG=True)
class TestSignup(TestCase):

    def setUp(self):
        self.client = APIClient()

    # User posts valid sign up data
    def test_signup_successful(self):
        signup_data = {
            'full_name': 'John Smith', 'email': 'john@example.com', 'username': 'johnsmith12',
            'phone': '+41524204242', 'hack_license': '123456', 'password': 'password',
            'password_confirm': 'password'
        }

        resp = self.client.post(reverse('users:signup'), data=signup_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)

    # User posts sign up data with missing full_name field
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

    # User posts valid sign up data and receives authorization token
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
        self.assertEqual(resp.data['token'], token.key)

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


class TestResetPassword(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)

    # User sends email and receives new password
    def test_password_reset(self):
        data = {'email': 'test@example.com'}
        self.client.post(reverse('users:reset_password'), data=data)
        self.assertEqual(len(mail.outbox), 1)

        new_password = mail.outbox[0].body.split()[-1]

        login_data = {'username': 'test@example.com', 'password': new_password}
        resp = self.client.post(reverse('users:login'), data=login_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['token'], self.token.key)


class TestChangePassword(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)

    # Unauthorized user tries to change password
    def test_login_required(self):
        data = {'email': 'test@example.com'}
        resp = self.client.post(reverse('users:change_password'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user sends request to change password
    def test_password_reset(self):
        self.client.force_authenticate(user=self.user)
        data = {'password': 'newpassword'}
        resp = self.client.post(reverse('users:change_password'), data=data)

        login_data = {'username': 'test@example.com', 'password': 'newpassword'}
        resp = self.client.post(reverse('users:login'), data=login_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['token'], self.token.key)


class AddFriendsFromContacts(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.friend = UserFactory()
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)

    # Unauthorized user tries to add friend
    def test_login_required(self):
        data = {'contacts': ['123-456-7890']}
        resp = self.client.post(reverse('users:add_friends_from_contacts'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user adds friend
    def test_add_friend(self):
        self.client.force_authenticate(user=self.user)
        data = {'contacts': [self.friend.phone]}
        self.client.post(reverse('users:add_friends_from_contacts'), data=data)
        self.assertEqual(self.user.friends.get(), self.friend)


class AddFriendsFromFacebook(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.friend = UserFactory(facebook_id='friend_id')
        self.client = APIClient()

    @patch('open_facebook.api.OpenFacebook.get', return_value={'id': 'user_id', 'data': []})
    def test_no_friends_added(self, _):
        self.client.force_authenticate(user=self.user)
        data = {'token': 'token', 'facebook_id': 'user_id'}
        self.client.post(reverse('users:add_friends_from_facebook'), data=data)
        self.assertEqual(self.user.friends.count(), 0)
        self.assertEqual(self.user.facebook_id, 'user_id')

    @patch('open_facebook.api.OpenFacebook.get', return_value={'id': 'user_id', 'data': [{'id': 'friend_id'}]})
    def test_add_friend_from_facebook(self, _):
        self.client.force_authenticate(user=self.user)
        data = {'token': 'token', 'facebook_id': 'user_id'}
        self.client.post(reverse('users:add_friends_from_facebook'), data=data)
        self.assertEqual(self.user.friends.get(), self.friend)
        self.assertEqual(self.user.facebook_id, 'user_id')


class TestUploadAvatar(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com', avatar=None)
        self.client = APIClient()

    # Unauthorized user tries to upload avatar
    def test_login_required(self):
        tmp_file = NamedTemporaryFile(suffix='.jpg')

        image = Image.new('RGB', (100, 100))
        image.save(tmp_file)

        data = {'avatar': tmp_file}
        resp = self.client.put(reverse('users:upload_avatar'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # User uploads avatar successfuly
    def test_upload_avatar(self):
        self.client.force_authenticate(user=self.user)
        tmp_file = NamedTemporaryFile(suffix='.jpg')

        image = Image.new('RGB', (100, 100))
        image.save(tmp_file)

        data = {'avatar': tmp_file}
        resp = self.client.put(reverse('users:upload_avatar'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.avatar.url.endswith('.jpg'))


class TestUserInfo(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com', avatar=None)
        self.client = APIClient()

    # Unauthorized user tries to profile's info
    def test_login_required(self):
        resp = self.client.get(reverse('users:info'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user retrieves profile's info successfully
    def test_user_info_retrieve(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('users:info'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['email'], self.user.email)

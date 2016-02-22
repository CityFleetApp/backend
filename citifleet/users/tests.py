from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import User


class TestSignup(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_signup_successful(self):
        signup_data = {
            'full_name': 'John Smith', 'email': 'john@example.com',
            'phone': '123456', 'hack_license': '123456', 'password': 'password'
        }

        resp = self.client.post(reverse('users:signup'), data=signup_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)

    def test_signup_unsuccessful(self):
        signup_data = {
            'email': 'john@example.com',
            'phone': '123456', 'hack_license': '123456', 'password': 'password'
        }

        resp = self.client.post(reverse('users:signup'), data=signup_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(resp.data, {'full_name': ['This field is required.']})

from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .models import Document
from .factories import DocumentFactory


class TestDocumentViewSet(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()

    # Unauthorized user tries to make a request to reports API
    def test_login_required(self):
        resp = self.client.get(reverse('documents:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.post(reverse('documents:api-list'), data={})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.delete(reverse('documents:api-detail', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user fetches list of his documents
    def test_list(self):
        DocumentFactory(user=self.user)
        DocumentFactory(user=self.user, document_type=Document.TLC_PLATE_NUMBER)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('documents:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    # Authorized post data to upload document
    def test_create_report(self):
        self.client.force_authenticate(user=self.user)

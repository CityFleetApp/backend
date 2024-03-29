from datetime import timedelta

from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory
from citifleet.users.models import User

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

    # Authorized user post data to upload document
    def test_upload_document(self):
        self.client.force_authenticate(user=self.user)
        doc = SimpleUploadedFile('insurance.doc', 'text', content_type='text/plain')
        data = {'file': doc, 'document_type': Document.INSURANCE,
                'expiry_date': (timezone.now().date() + timedelta(days=30)).isoformat()}

        resp = self.client.post(reverse('documents:api-list'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        document = Document.objects.get()
        self.assertEqual(document.user, self.user)
        self.assertEqual(document.document_type, Document.INSURANCE)

    # Authorized user updates existing document
    def test_update_document(self):
        self.client.force_authenticate(user=self.user)
        document = DocumentFactory(user=self.user)
        doc = SimpleUploadedFile('insurance.doc', 'text', content_type='text/plain')
        data = {'expiry_date': (timezone.now().date() + timedelta(days=15)).isoformat(),
                'file': doc, 'document_type': Document.INSURANCE}
        resp = self.client.put(reverse('documents:api-detail', args=[document.id]), data=data)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Document.objects.get().expiry_date, timezone.now().date() + timedelta(days=15))

    # Authorized user get list with expired document and has appropriate status
    def test_expired_document(self):
        self.client.force_authenticate(user=self.user)
        DocumentFactory(user=self.user, document_type=Document.DMV_LICENSE,
                        expiry_date=timezone.now() + timedelta(days=15), status=Document.CONFIRMED)
        resp = self.client.get(reverse('documents:api-list'))
        self.assertEqual(resp.data[0]['expired'], False)
        self.assertEqual(User.objects.get(id=self.user.id).documents_up_to_date, True)

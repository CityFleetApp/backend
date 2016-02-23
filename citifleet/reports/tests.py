from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .models import Report
from .factories import ReportFactory


class TestReportViewSet(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()

    def test_login_required(self):
        resp = self.client.get(reverse('reports:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.post(reverse('reports:api-list'), data={})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.delete(reverse('reports:api-detail', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.post(reverse('reports:api-confirm-report', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_list(self):
        ReportFactory.create_batch(10)
        self.client.login(username='test@example.com', password='password')
        resp = self.client.get(reverse('reports:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)

    def test_create_report(self):
        self.client.login(username='test@example.com', password='password')
        report_data = {'report_type': Report.POLICE, 'lat': 47.0, 'lng': 51.0}
        resp = self.client.post(reverse('reports:api-list'), data=report_data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

        report = Report.objects.get()
        self.assertEqual(report.report_type, Report.POLICE)
        self.assertEqual(report.location.x, 47.0)
        self.assertEqual(report.location.y, 51.0)

    def test_delete_report(self):
        report = ReportFactory()
        self.client.login(username='test@example.com', password='password')
        resp = self.client.delete(reverse('reports:api-detail', args=[report.id]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Report.objects.count(), 0)

    def test_confirm_report(self):
        report = ReportFactory()
        self.client.login(username='test@example.com', password='password')
        resp = self.client.post(reverse('reports:api-confirm-report', args=[report.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(report.updated, Report.objects.get().updated)

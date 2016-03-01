from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point
from django.test.utils import override_settings

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .models import Report
from .factories import ReportFactory
from .tasks import delete_unconfirmed_reports


class TestReportViewSet(TestCase):

    def setUp(self):
        self.point = Point(-47.0, -47.0)
        self.user = UserFactory(email='test@example.com', location=self.point)
        self.client = APIClient()

    # Unauthorized user tries to make a request to reports API
    def test_login_required(self):
        resp = self.client.get(reverse('reports:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.post(reverse('reports:api-list'), data={})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.delete(reverse('reports:api-detail', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.post(reverse('reports:api-confirm-report', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user fetches list of nearby reports
    def test_list(self):
        ReportFactory.create_batch(10, location=self.point)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('reports:api-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)

    # Authorized post data to create a new report
    def test_create_report(self):
        self.client.force_authenticate(user=self.user)
        report_data = {'report_type': Report.POLICE, 'lat': 47.0, 'lng': 51.0}
        resp = self.client.post(reverse('reports:api-list'), data=report_data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

        report = Report.objects.get()
        self.assertEqual(report.report_type, Report.POLICE)
        self.assertEqual(report.location.x, 47.0)
        self.assertEqual(report.location.y, 51.0)

    # Authorized user deletes report by it's id
    def test_delete_report(self):
        report = ReportFactory(location=self.point)
        self.client.force_authenticate(user=self.user)
        resp = self.client.delete(reverse('reports:api-detail', args=[report.id]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Report.objects.count(), 0)

    # Authorized user confirms report and it's updated value is changed
    def test_confirm_report(self):
        report = ReportFactory(location=self.point)
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(reverse('reports:api-confirm-report', args=[report.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(report.updated, Report.objects.get().updated)

    # Outdated task is deleted
    @override_settings(AUTOCLOSE_INTERVAL=0)
    def test_unconfirmed_report_removed(self):
        ReportFactory()
        delete_unconfirmed_reports()
        self.assertEqual(Report.objects.count(), 0)

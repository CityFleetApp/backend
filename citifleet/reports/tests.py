from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point
from django.test.utils import override_settings

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from mock import patch
from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.factories import UserFactory

from .models import Report
from .factories import ReportFactory
from .tasks import delete_unconfirmed_reports


class TestNearbyReportViewSet(TestCase):

    def setUp(self):
        self.point = Point(-47.0, -47.0)
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()

    # Unauthorized user tries to make a request to reports API
    def test_login_required(self):
        resp = self.client.get(reverse('reports:nearby-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.post(reverse('reports:nearby-list'), data={})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.delete(reverse('reports:nearby-detail', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        resp = self.client.post(reverse('reports:nearby-confirm-report', args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user fetches list of nearby reports
    def test_list(self):
        ReportFactory.create_batch(10, location=self.point)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('{}{}'.format(reverse('reports:nearby-list'), '?lat=-47.0&lng=-47.0'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)
        self.assertEqual(self.user.location.x, -47.0)
        self.assertEqual(self.user.location.y, -47.0)

    # Authorized post data to create a new report
    def test_create_report(self):
        self.client.force_authenticate(user=self.user)
        report_data = {'report_type': Report.POLICE, 'lat': 47.0, 'lng': 51.0}
        resp = self.client.post(reverse('reports:nearby-list'), data=report_data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)

        report = Report.objects.get()
        self.assertEqual(report.report_type, Report.POLICE)
        self.assertEqual(report.location.x, 47.0)
        self.assertEqual(report.location.y, 51.0)

    # Authorized user deletes report by it's id
    def test_deny_report(self):
        report = ReportFactory(location=self.point)
        timestamp = report.updated
        self.client.force_authenticate(user=self.user)

        resp = self.client.post(reverse('reports:nearby-deny-report', args=[report.id]))
        report.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(report.updated, timestamp)
        self.assertTrue(report.not_here)
        self.assertEqual(report.declined, self.user)

        resp = self.client.post(reverse('reports:nearby-deny-report', args=[report.id]))
        report.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(report.updated, timestamp)
        self.assertTrue(report.not_here)
        self.assertEqual(report.declined, self.user)

        user2 = UserFactory(email='test2@example.com')
        self.client.force_authenticate(user=user2)
        resp = self.client.post(reverse('reports:nearby-deny-report', args=[report.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Report.objects.filter(id=report.id).exists())

    # Authorized user confirms report and it's updated value is changed
    def test_confirm_report(self):
        report = ReportFactory(location=self.point)
        timestamp = report.updated
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(reverse('reports:nearby-confirm-report', args=[report.id]))

        report.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(report.updated, timestamp)
        self.assertFalse(report.not_here)
        self.assertEqual(report.declined, None)

    # Outdated task is deleted
    @override_settings(AUTOCLOSE_INTERVAL=0)
    def test_unconfirmed_report_removed(self):
        ReportFactory()
        delete_unconfirmed_reports()
        self.assertEqual(Report.objects.count(), 0)


class TestMapReportViewSet(TestCase):

    def setUp(self):
        self.user_point = Point(-50.0, -50.0)
        self.point = Point(-47.0, -47.0)
        self.user = UserFactory(email='test@example.com', location=self.user_point)
        self.client = APIClient()

    # Authorized user fetches list of nearby reports
    def test_list(self):
        ReportFactory.create_batch(10, location=self.point)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('{}{}'.format(reverse('reports:map-list'), '?lat=-47.0&lng=-47.0'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)
        self.assertEqual(self.user.location.x, -50.0)
        self.assertEqual(self.user.location.y, -50.0)


class TestPushNotificationSent(TestCase):

    def setUp(self):
        self.user_point = Point(-50.0, -50.0)
        self.point = Point(-50.0, -50.0)
        self.user = UserFactory(email='test@example.com', location=self.user_point)
        self.client = APIClient()
        self.report = ReportFactory(location=self.point)
        self.apns = APNSDevice.objects.create(user=self.user)
        self.gcm = GCMDevice.objects.create(user=self.user)

    # Push notification sent on report creation
    @patch('push_notifications.apns.apns_send_bulk_message')
    @patch('push_notifications.gcm.gcm_send_bulk_message')
    def test_push_sent_on_new_report(self, gcm_mock, apns_mock):
        report = ReportFactory(location=self.point)
        self.assertEqual(apns_mock.call_count, 1)
        apns_mock.assert_called_with(
            alert={'action': 'added', 'id': report.id, 'lat': self.report.location.x,
                   'lng': self.report.location.y, 'type': report.report_type},
            registration_ids=[''])
        self.assertEqual(gcm_mock.call_count, 1)
        gcm_mock.assert_called_with(
            data={'message': {'action': 'added', 'id': report.id, 'lat': self.report.location.x,
                  'lng': self.report.location.y, 'type': report.report_type}},
            registration_ids=[''])

    # Push notification sent on report delete
    @patch('push_notifications.apns.apns_send_bulk_message')
    @patch('push_notifications.gcm.gcm_send_bulk_message')
    def test_push_sent_on_report_remove(self, gcm_mock, apns_mock):
        report_id = self.report.id
        self.report.delete()
        apns_mock.assert_called_with(
            alert={'action': 'removed', 'id': report_id, 'lat': self.report.location.x,
                   'lng': self.report.location.y, 'type': self.report.report_type}, registration_ids=[''])
        gcm_mock.assert_called_with(
            data={'message': {'action': 'removed', 'id': report_id, 'lat': self.report.location.x,
                  'lng': self.report.location.y, 'type': self.report.report_type}}, registration_ids=[''])

    # Push notification not sent for not nearby drivers
    @patch('push_notifications.apns.apns_send_bulk_message')
    @patch('push_notifications.gcm.gcm_send_bulk_message')
    def test_push_not_sent(self, gcm_mock, apns_mock):
        report = ReportFactory(location=Point(20, 20))
        self.assertEqual(apns_mock.call_count, 0)
        self.assertEqual(gcm_mock.call_count, 0)

        report.delete()
        self.assertEqual(apns_mock.call_count, 0)
        self.assertEqual(gcm_mock.call_count, 0)

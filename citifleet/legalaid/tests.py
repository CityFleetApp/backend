from django.core.urlresolvers import reverse

from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from citifleet.users.factories import UserFactory

from .factories import (InsuranceBrokerFactory, AccountingFactory, DMVLawyerFactory,
                        TLCLawyerFactory, LocationFactory)


class TestInsuranceViewSet(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()

    # Unauthorized user requests list of insurance brokers
    def test_login_required(self):
        resp = self.client.get(reverse('legalaid:insurance-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user requests list of insurance brokers
    def test_list(self):
        InsuranceBrokerFactory.create_batch(10)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('legalaid:insurance-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)


class TestAccountingViewSet(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()

    # Unauthorized user requests list of accounting services
    def test_login_required(self):
        resp = self.client.get(reverse('legalaid:accounting-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user requests list of accounting services
    def test_list(self):
        AccountingFactory.create_batch(10)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('legalaid:accounting-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)


class TestDMVLawyerViewSet(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()

    # Unauthorized user requests list of DMV lawyers
    def test_login_required(self):
        resp = self.client.get(reverse('legalaid:dmv_lawyers-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user requests list of DMV lawyers
    def test_list(self):
        DMVLawyerFactory.create_batch(10)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('legalaid:dmv_lawyers-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)


class TestTLCLawyerViewSet(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()

    # Unauthorized user requests list of TLC lawyers
    def test_login_required(self):
        resp = self.client.get(reverse('legalaid:tlc_lawyers-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # Authorized user requests list of TLC lawyers
    def test_list(self):
        TLCLawyerFactory.create_batch(10)
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('legalaid:tlc_lawyers-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)


class TestFilterLocation(TestCase):

    def setUp(self):
        self.user = UserFactory(email='test@example.com')
        self.client = APIClient()
        self.location1 = LocationFactory(name='Bronx')
        self.location2 = LocationFactory(name='Queens')
        DMVLawyerFactory.create_batch(5, location=self.location1)
        DMVLawyerFactory.create_batch(10, location=self.location2)

    # User retrieves list of locations
    def test_location_list(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse('legalaid:locations-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    # User filters lawyers by location id
    def test_filter(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('{}?location={}'.format(reverse('legalaid:dmv_lawyers-list'), self.location1.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 5)

        resp = self.client.get('{}?location={}'.format(reverse('legalaid:dmv_lawyers-list'), self.location2.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)

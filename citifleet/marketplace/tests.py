from tempfile import NamedTemporaryFile

from django.core.urlresolvers import reverse

from mock import patch
from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.factories import UserFactory

from .models import JobOffer
from .factories import CarMakeFactory, CarModelFactory, JobOfferFactory


class TestMarketPlaceViewSet(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.make = CarMakeFactory()
        self.model = CarModelFactory(make=self.make)

    def test_login_required(self):
        resp = self.client.get(reverse('marketplace:sale-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_car(self):
        self.client.force_authenticate(user=self.user)

        tmp_file1 = NamedTemporaryFile(suffix='.jpg')
        image = Image.new('RGB', (100, 100))
        image.save(tmp_file1)

        tmp_file2 = NamedTemporaryFile(suffix='.jpg')
        image = Image.new('RGB', (100, 100))
        image.save(tmp_file2)

        data = {
            'make': self.make.id, 'model': self.model.id, 'type': 1, 'color': 1, 'year': 2012,
            'fuel': 1, 'seats': 5, 'price': 5000, 'description': 'Text',
            'photos': [tmp_file1, tmp_file2]
        }

        resp = self.client.post(reverse('marketplace:postings-rent-list'), data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class TestJobOfferProcess(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.apns = APNSDevice.objects.create(user=self.user)
        self.gcm = GCMDevice.objects.create(user=self.user)

    @patch('push_notifications.apns.apns_send_bulk_message')
    @patch('push_notifications.gcm.gcm_send_bulk_message')
    def test_push_sent_on_job_award(self, gcm_mock, apns_mock):
        self.client.force_authenticate(user=self.user)
        self.job_owner = UserFactory()

        offer = JobOfferFactory(driver=self.user, status=JobOffer.AVAILABLE, owner=self.job_owner)
        offer.award(self.user)

        offer.refresh_from_db()
        self.assertEqual(offer.status, JobOffer.COVERED)
        self.assertEqual(offer.driver, self.user)

        gcm_mock.assert_called_with(
            data={'message': {'id': offer.id, 'type': 'offer_covered', 'title': 'Your job offer accepted'}},
            registration_ids=[''])
        apns_mock.assert_called_with(
            alert={'id': offer.id, 'type': 'offer_covered', 'title': 'Your job offer accepted'},
            registration_ids=[''])

    def test_job_complete(self):
        self.client.force_authenticate(user=self.user)
        self.job_owner = UserFactory()

        offer = JobOfferFactory(driver=self.user, status=JobOffer.COVERED, owner=self.job_owner)
        resp = self.client.post(reverse('marketplace:marketplace-offers-complete-job', args=[offer.id]),
                                data={'rating': 4, 'paid_on_time': True})
        offer.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(offer.status, JobOffer.COMPLETED)
        self.assertEqual(offer.paid_on_time, True)
        self.assertEqual(offer.owner_rating, 4)

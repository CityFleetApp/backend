from io import BytesIO

from django.core.urlresolvers import reverse

from mock import patch
from test_plus.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
from push_notifications.models import APNSDevice, GCMDevice

from citifleet.users.factories import UserFactory

from .models import JobOffer
from .factories import CarMakeFactory, CarModelFactory, JobOfferFactory, CarColorFactory


class TestMarketPlaceViewSet(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.make = CarMakeFactory()
        self.model = CarModelFactory(make=self.make)
        self.color = CarColorFactory()

    def test_login_required(self):
        resp = self.client.get(reverse('marketplace:sale-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_car(self):
        self.client.force_authenticate(user=self.user)

        file1 = BytesIO()
        image = Image.new('RGB', size=(100, 100))
        image.save(file1, 'png')
        file1.name = 'test1.jpg'
        file1.seek(0)

        file2 = BytesIO()
        image = Image.new('RGB', size=(100, 100))
        image.save(file2, 'png')
        file2.name = 'test2.jpg'
        file2.seek(0)

        data = {
            'make': self.make.id, 'model': self.model.id, 'type': 1, 'color': self.color.id, 'year': 2012,
            'fuel': 1, 'seats': 5, 'price': 5000, 'description': 'Text',
            'photos': [file1, file2]
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

    def test_job_offer_list(self):
        self.client.force_authenticate(user=self.user)
        JobOfferFactory.create_batch(30, status=JobOffer.COVERED, owner=self.user)
        JobOfferFactory.create_batch(40, status=JobOffer.AVAILABLE, owner=self.user)

        resp = self.client.get(reverse('marketplace:marketplace-offers-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['available'], 40)

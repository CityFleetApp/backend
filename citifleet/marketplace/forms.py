from django import forms

from .models import JobOffer, GeneralGood


class AvailableJobOfferAdminForm(forms.ModelForm):

    class Meta:
        model = JobOffer
        exclude = ['driver_requests', 'owner', 'status', 'driver']


class GeneralGoodAdminForm(forms.ModelForm):

    class Meta:
        model = GeneralGood
        exclude = ['owner']

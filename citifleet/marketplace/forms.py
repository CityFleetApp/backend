from django import forms

from .models import JobOffer


class AvailableJobOfferAdminForm(forms.ModelForm):

    class Meta:
        model = JobOffer
        exclude = ['driver_requests', 'owner', 'status', 'driver']

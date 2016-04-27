from django import forms

from citifleet.payments.utils import calculate_fee

from .models import JobOffer


class AvailableJobOfferAdminForm(forms.ModelForm):

    class Meta:
        model = JobOffer
        exclude = ['driver_requests', 'owner', 'status', 'driver']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AvailableJobOfferAdminForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AvailableJobOfferAdminForm, self).clean()
        if self.request.user.is_superuser:
            return cleaned_data

        amount = cleaned_data['fare']
        fee = calculate_fee(amount, 'offer')

        if self.instance is None and self.request.user.balance < fee:
            raise forms.ValidationError('Insufficient funds. Please refill balance')

        return cleaned_data

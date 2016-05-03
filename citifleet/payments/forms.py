from django import forms
from django.contrib.admin import widgets


class RegisterCardForm(forms.Form):
    number = forms.CharField()
    expiry = forms.DateField(widget=widgets.AdminDateWidget())
    cvv2 = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()

    def clean(self):
        cd = super(RegisterCardForm, self).clean()

        number = cd.get('number')
        expiry_date = cd.get('expiry')

        if number:
            if number[0] == '4':
                cd['type'] = 'visa'
            else:
                cd['type'] = 'mastercard'

        if expiry_date:
            cd.pop('expiry')
            cd['expire_month'] = expiry_date.month
            cd['expire_year'] = expiry_date.year
        return cd

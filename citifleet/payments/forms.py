from django import forms


class RegisterCardForm(forms.Form):
    number = forms.IntegerField()
    expiry = forms.DateField()
    cvv2 = forms.IntegerField()
    first_name = forms.CharField()
    last_name = forms.CharField()

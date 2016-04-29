from django.views.generic import FormView

from paypalrestsdk import CreditCard

from .forms import RegisterCardForm


class RegisterCardView(FormView):
    form_class = RegisterCardForm

    def form_valid(self, form):
        credit_card = CreditCard({
            "type": "visa",
            "number": "4417119669820331",
            "expire_month": "11",
            "expire_year": "2018",
            "cvv2": "874",
            "first_name": "Joe",
            "last_name": "Shopper"})

        if credit_card.create() and credit_card['state'] == 'ok':
            print('Save credit card %s' % credit_card.id)

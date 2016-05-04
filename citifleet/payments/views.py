from django.views.generic import FormView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from paypalrestsdk import CreditCard

from .forms import RegisterCardForm


class RegisterCardView(FormView):
    form_class = RegisterCardForm
    template_name = 'payments/register_card.html'

    def form_valid(self, form):
        credit_card = CreditCard(form.cleaned_data)
        if credit_card.create() and credit_card['state'] == 'ok':
            print(credit_card)
            self.request.user.card_id = credit_card['id']
            self.request.user.save()
            messages.add_message(self.request, messages.SUCCESS, 'Card registered')
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            messages.add_message(self.request, messages.ERROR, 'Card registration failed')
            return self.render_to_response(self.get_context_data(form=form))

register_card = RegisterCardView.as_view()

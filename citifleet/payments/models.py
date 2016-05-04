from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from paypalrestsdk import Payment


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    amount = models.DecimalField(_('Amount'), max_digits=6, decimal_places=2)
    created = models.DateTimeField(_('Created'), auto_now_add=True)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

    def __unicode__(self):
        return '{} paid {}$ on {}'.format(self.user.full_name, self.amount, self.created.strftime('%d/%m/%Y %H:%M'))


class PaymentSetting(models.Model):
    OFFERS = 1
    GOODS = 2
    CARS = 3

    SECTION_CHOICES = (
        (OFFERS, _('Offers')),
        (GOODS, _('Goods')),
        (CARS, _('Cars')),
    )

    FIXED = 1
    PERCENTAGE = 2

    PAYMENT_CHOICES = (
        (FIXED, _('Fixed')),
        (PERCENTAGE, _('Percentage')),
    )

    marketplace_section = models.PositiveSmallIntegerField(_('Marketplace Section'), choices=SECTION_CHOICES)
    payment_type = models.PositiveSmallIntegerField(_('Payment type'), choices=PAYMENT_CHOICES)
    amount = models.DecimalField(_('Amount'), max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = _('Payment Setting')
        verbose_name_plural = _('Payment Settings')

    def __unicode__(self):
        return '{} {}'.format(self.get_marketplace_section_display(), self.get_payment_type_display())

    @staticmethod
    def charge_user(user, section_type, amount):
        setting = PaymentSetting.objects.get(marketplace_section=section_type)

        if setting.payment_type == PaymentSetting.FIXED:
            charged_amount = setting.amount
        else:
            charged_amount = amount * setting.amount / 100

        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "credit_card",
                "funding_instruments": [{
                    "credit_card_token": {
                        "credit_card_id": user.card_id
                    }
                }]
            },
            "transactions": [{
                "amount": {
                    "total": "{}".format(charged_amount),
                    "currency": "USD"
                },
                "description": "Cityfleet payment for markeplace posting."
            }]
        })

        if payment.create():
            print('True')
            return payment.to_dict()
        else:
            print('False')
            return payment.to_dict()

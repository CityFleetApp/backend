from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    amount = models.DecimalField(_('Amount'), max_digits=6, decimal_places=2)
    created = models.DateTimeField(_('Created'), auto_now_add=True)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

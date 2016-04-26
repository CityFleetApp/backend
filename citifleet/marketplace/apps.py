from __future__ import unicode_literals

from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    name = 'citifleet.marketplace'

    def ready(self):
        from . import signals

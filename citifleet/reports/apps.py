from __future__ import unicode_literals

from django.apps import AppConfig


class ReportsConfig(AppConfig):
    name = 'citifleet.reports'

    def ready(self):
        from . import signals
        from citifleet.reports import tasks

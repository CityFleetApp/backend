from __future__ import unicode_literals

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'citifleet.notifications'

    def ready(self):
        from . import signals

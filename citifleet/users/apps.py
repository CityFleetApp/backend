from __future__ import unicode_literals

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'citifleet.users'

    def ready(self):
        from . import signals


from __future__ import unicode_literals

from django.apps import AppConfig


class ChatConfig(AppConfig):
    name = 'citifleet.chat'

    def ready(self):
        from . import signals

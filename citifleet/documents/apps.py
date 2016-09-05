from __future__ import unicode_literals

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    name = 'citifleet.documents'
    verbose_name = 'Documents'

    def ready(self):
        from citifleet.documents import tasks

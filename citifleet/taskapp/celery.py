
from __future__ import absolute_import
import os
from celery import Celery
from django.apps import AppConfig, apps
from django.conf import settings


if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


app = Celery('citifleet')


class CeleryConfig(AppConfig):
    name = 'citifleet.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        app.config_from_object('django.conf:settings')
        app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()], force=True)

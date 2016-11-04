# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework.routers import SimpleRouter
from django.conf.urls import url, include

from citifleet.fcm_notifications import views

device_router = SimpleRouter()
device_router.register(r'', views.FCMDeviceViewSet)

urlpatterns = [
    url(r'^', include(device_router.urls)),
]

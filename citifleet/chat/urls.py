# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'', views.RoomViewSet, base_name='api')

urlpatterns = [
    url(r'^new/$', views.new_room, name='new_room'),
    url(r'^(?P<label>[\d]+)/$', views.chat_room, name='chat_room'),
    url(r'^', include(router.urls)),
]

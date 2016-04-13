# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'rooms', views.RoomViewSet, base_name='rooms')
router.register(r'friends', views.FriendsViewSet, base_name='friends')

urlpatterns = [
    url(r'^', include(router.urls)),
]

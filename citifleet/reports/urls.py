# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'nearby', views.NearbyReportViewSet, base_name='nearby')
router.register(r'map', views.MapReportViewSet, base_name='map')


urlpatterns = [
    url(r'^', include(router.urls))
]

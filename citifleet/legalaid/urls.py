# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'insurance/', views.BrokerViewSet, base_name='insurance')
router.register(r'accouting/', views.AccountingViewSet, base_name='accounting')


urlpatterns = [
    url(r'^', include(router.urls))
]

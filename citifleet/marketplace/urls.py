# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'sale', views.CarSaleModelViewSet, base_name='sale')
router.register(r'rent', views.CarRentModelViewSet, base_name='rent')
router.register(r'model', views.CarModelViewSet, base_name='model')
router.register(r'make', views.CarMakeViewSet, base_name='make')


urlpatterns = [
    url(r'^/cars/', include(router.urls)),
]

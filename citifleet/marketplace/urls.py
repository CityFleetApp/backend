# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'posting/rent', views.PostCarRentViewSet, base_name='postings-rent')
router.register(r'posting/sale', views.PostCarSaleViewSet, base_name='postings-sale')
router.register(r'sale', views.CarSaleModelViewSet, base_name='sale')
router.register(r'rent', views.CarRentModelViewSet, base_name='rent')
router.register(r'model', views.CarModelViewSet, base_name='model')
router.register(r'make', views.CarMakeViewSet, base_name='make')


urlpatterns = [
    url(r'^/cars/', include(router.urls)),
    url(r'^/fuel/$', views.fuel_types, name='fuel'),
    url(r'^/types/$', views.car_types, name='types'),
    url(r'^/colors/$', views.colors, name='colors'),
    url(r'^/seats/$', views.seats, name='seats'),
]

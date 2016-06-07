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

goods_router = DefaultRouter()
goods_router.register(r'/posting', views.PostingGeneralGoodsViewSet, base_name='postings-goods')
goods_router.register(r'', views.MarketGeneralGoodsViewSet, base_name='marketplace-goods')

offers_router = DefaultRouter()
offers_router.register(r'/posting', views.PostingJobOfferViewSet, base_name='postings-offers')
offers_router.register(r'', views.MarketJobOfferViewSet, base_name='marketplace-offers')

car_photos_router = DefaultRouter()
car_photos_router.register(r'', views.CarPhotoViewSet, base_name='carphotos')

goods_photos_router = DefaultRouter()
goods_photos_router.register(r'', views.GoodsPhotoViewSet, base_name='goodsphotos')

colors_router = DefaultRouter()
colors_router.register(r'', views.CarColorViewSet, base_name='colors')

urlpatterns = [
    url(r'^/cars/', include(router.urls)),
    url(r'^/goods', include(goods_router.urls)),
    url(r'^/offers', include(offers_router.urls)),
    url(r'^/carphotos', include(car_photos_router.urls)),
    url(r'^/goodsphotos', include(goods_photos_router.urls)),
    url(r'^/fuel/$', views.fuel_types, name='fuel'),
    url(r'^/types/$', views.car_types, name='types'),
    url(r'^/colors', include(colors_router.urls)),
    url(r'^/seats/$', views.seats, name='seats'),
    url(r'^/vehicles/$', views.vehicle_choices, name='vehicles'),
    url(r'^/job_types/$', views.job_types, name='job_types'),
    url(r'^/manage-posts/$', views.manage_posts, name='manage_posts'),
    url(r'^/award-job/(?P<job_id>\d+)/(?P<driver_id>\d+)/$', views.award_job, name='award_job'),
]

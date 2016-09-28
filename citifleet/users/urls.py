# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet

from citifleet.common import views as common_views
from . import views

router = DefaultRouter()
router.register(r'', views.PhotoModelViewSet, base_name='photos')

device_router = DefaultRouter()
device_router.register(r'device/apns', common_views.APNSDeviceAuthorizedViewSet)
device_router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)

friends_photos = DefaultRouter()
friends_photos.register(r'', views.FriendPhotoModelViewSet, base_name='friends_photos')

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.login, name='login'),
    url(r'^reset-password/$', views.reset_password, name='reset_password'),
    url(r'^change-password/$', views.change_password, name='change_password'),
    url(r'^add-contacts-friends/$', views.add_contacts_friends, name='add_friends_from_contacts'),
    url(r'^add-facebook-friends/$', views.add_facebook_friends, name='add_friends_from_facebook'),
    url(r'^add-twitter-friends/$', views.add_twitter_friends, name='add_friends_from_twitter'),
    url(r'^add-instagram-friends/$', views.add_instagram_friends, name='add_friends_from_instagram'),
    url(r'^upload-avatar/$', views.upload_avatar, name='upload_avatar'),
    url(r'^info/$', views.info, name='info'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^photos', include(router.urls)),
    url(r'^devices', include(device_router.urls)),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^person/(?P<id>\d+)/photos', include(friends_photos.urls)),
    url(r'^person/(?P<id>\d+)/', views.friend, name='friend'),
    url(r'^send_mass_push_notification/$', views.send_mass_push_notification, name='send_mass_push_notification'),
    url(r'^username/check/$', views.CheckUsernameInUseApiView.as_view(), name='check_username_in_use'),
    url(r'^location/update/$', views.update_user_location, name='update_user_location'),
]

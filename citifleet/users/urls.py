# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.login, name='login'),
    url(r'^reset-password/$', views.reset_password, name='reset_password'),
    url(r'^change-password/$', views.change_password, name='change_password'),
    url(r'^add-contacts-friends/$', views.add_contacts_friends, name='add_friends_from_contacts'),
    url(r'^add-facebook-friends/$', views.add_facebook_friends, name='add_friends_from_facebook'),
    url(r'^add-twitter-friends/$', views.add_twitter_friends, name='add_friends_from_twitter'),
    url(r'^add-instagram-friends/$', views.add_instagram_friends, name='add_friends_from_instagram'),
]

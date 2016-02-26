# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', obtain_auth_token, name='login'),
    url(r'^reset-password/$', views.reset_password, name='reset_password'),
    url(r'^change-password/$', views.change_password, name='change_password'),
]

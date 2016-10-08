# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from citifleet.fcm_notifications.models import FCMDevice


admin.site.register(FCMDevice)

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth import get_user_model

from citifleet.fcm_notifications.models import FCMDevice

User = get_user_model()


@admin.register(FCMDevice)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'device_id', 'user', 'active', 'date_created')
    list_filter = ('active', )
    raw_id_fields = ('user', )
    search_fields = ('name', 'device_id', 'user__username')

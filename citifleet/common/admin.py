# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from push_notifications.models import APNSDevice
from push_notifications.admin import DeviceAdmin

from django.contrib import admin

from citifleet.common.models import CustomAPNSDevice

admin.site.unregister(APNSDevice)
admin.site.register(CustomAPNSDevice, DeviceAdmin)

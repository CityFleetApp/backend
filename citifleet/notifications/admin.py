from django.contrib import admin

from .models import Notification, MassNotification


admin.site.register(Notification)
admin.site.register(MassNotification)

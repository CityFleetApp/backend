from django.contrib import admin
from django.contrib import messages

from .models import Notification, MassNotification, NotificationTemplate


class NotificationTemplateModelAdmin(admin.ModelAdmin):
    list_display = ('type', 'title', 'enabled')
    list_filter = ('enabled',)
    actions = ('enable_notifications', 'disable_notifications')

    def enable_notifications(self, request, queryset):
        queryset.update(enabled=True)
        messages.add_message(request, messages.SUCCESS, 'Notifications successfully enabled')
    enable_notifications.short_description = 'Enable selected notifications'

    def disable_notifications(self, request, queryset):
        queryset.update(enabled=False)
        messages.add_message(request, messages.SUCCESS, 'Notifications successfully disabled')
    disable_notifications.short_description = 'Disable selected notifications'

admin.site.register(Notification)
admin.site.register(MassNotification)
admin.site.register(NotificationTemplate, NotificationTemplateModelAdmin)

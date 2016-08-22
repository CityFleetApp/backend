from django.contrib import admin

from .models import Report


class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'latitude', 'longitude', 'report_type']

    def latitude(self, obj):
        return obj.location.x

    def longitude(self, obj):
        return obj.location.y

admin.site.register(Report, ReportAdmin)

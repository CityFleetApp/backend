from django.contrib import admin

from .models import Report


class ReportAdmin(admin.ModelAdmin):
    change_list_template = 'reports/admin_list.html'


admin.site.register(Report, ReportAdmin)

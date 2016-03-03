# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),
    url(r'^api/users', include('citifleet.users.urls', namespace='users')),
    url(r'^api/reports', include('citifleet.reports.urls', namespace='reports')),
    url(r'^api/legalaid', include('citifleet.legalaid.urls', namespace='legalaid')),
    url(r'^api/documents', include('citifleet.documents.urls', namespace='documents')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

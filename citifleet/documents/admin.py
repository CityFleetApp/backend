from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Document


class DocumentModelAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'user__hack_license', 'user__phone', 'user__full_name')
    list_display = ('user', 'document_type', 'status', 'expired', 'file', 'document_preview')
    list_filter = ('status', 'document_type')
    actions = ['make_declined', 'make_confirmed']

    def make_declined(self, request, queryset):
        queryset.update(status=Document.DECLINED)
    make_declined.short_description = 'Mark selected documents as declined'

    def make_confirmed(self, request, queryset):
        queryset.update(status=Document.CONFIRMED)
    make_confirmed.short_description = 'Mark selected documents as confirmed'

    def document_preview(self, obj):
        return mark_safe('<img alt="file" src="{}" width="150" height="150"/>'.format(obj.file.url))

admin.site.register(Document, DocumentModelAdmin)

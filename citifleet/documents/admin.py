from django.contrib import admin

from .models import Document


class DocumentModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'status', 'expired')
    list_filter = ('status', 'document_type')
    actions = ['make_declined', 'make_confirmed']

    def make_declined(self, request, queryset):
        queryset.update(status=Document.DECLINED)
    make_declined.short_description = 'Mark selected documents as declined'

    def make_confirmed(self, request, queryset):
        queryset.update(status=Document.CONFIRMED)
    make_confirmed.short_description = 'Mark selected documents as confirmed'

admin.site.register(Document, DocumentModelAdmin)

from django.contrib import admin

from .models import PaymentSetting, Transaction


class BalanceMixin(object):

    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super(BalanceMixin, self).get_form(request, obj, **kwargs)

        class FormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return FormWithRequest


class TransactionModelAdmin(admin.ModelAdmin):
    # TODO: prevent from editing

    def get_actions(self, request):
        if not request.user.is_superuser:
            return []
        else:
            return super(TransactionModelAdmin, self).get_actions(request)

    def get_list_display_links(self, request, list_display):
        if not request.user.is_superuser:
            return None
        else:
            return super(TransactionModelAdmin, self).get_list_display_links(request, list_display)

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ['user', 'amount', 'created']
        else:
            return ['amount', 'created']

    def get_queryset(self, request):
        qs = super(TransactionModelAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user=request.user)
        else:
            return qs

admin.site.register(Transaction, TransactionModelAdmin)
admin.site.register(PaymentSetting)

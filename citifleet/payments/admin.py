class BalanceMixin(object):

    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super(BalanceMixin, self).get_form(request, obj, **kwargs)

        class FormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return FormWithRequest

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect

from citifleet.payments.models import PaymentSetting, Transaction
from .models import CarModel, CarMake, Car, GeneralGood, GoodPhoto, CarPhoto, JobOffer, CarColor
from .forms import AvailableJobOfferAdminForm, GeneralGoodAdminForm


class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    min_num = 1
    max_num = 1
    extra = 1


class CarModelModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'make']
    list_filter = ['make']


class CarModelAdmin(admin.ModelAdmin):
    list_display = ['model', 'make', 'type', 'year', 'fuel', 'seats', 'price']
    list_filter = ['make', 'model', 'type', 'fuel', 'seats']
    inlines = [CarPhotoInline]

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            result = PaymentSetting.charge_user(request.user, PaymentSetting.CARS, obj.price)
            if result.get('state', None) == 'approved':
                Transaction.objects.create(user=request.user, amount=obj.price)
            else:
                messages.add_message(request, messages.ERROR, 'Per-posting charge failed')
                return HttpResponseRedirect(reverse('admin:index'))

        obj.owner = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(CarModelAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(owner=request.user)
        else:
            return qs


class GoodPhotoInline(admin.TabularInline):
    model = GoodPhoto
    min_num = 1
    max_num = 1
    extra = 1


class GeneralGoodsModelAdmin(admin.ModelAdmin):
    inlines = [GoodPhotoInline]
    form = GeneralGoodAdminForm

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            result = PaymentSetting.charge_user(request.user, PaymentSetting.GOODS, obj.price)
            if result.get('state', None) == 'approved':
                Transaction.objects.create(user=request.user, amount=obj.price)
            else:
                messages.add_message(request, messages.ERROR, 'Per-posting charge failed')
                return HttpResponseRedirect(reverse('admin:index'))

        obj.owner = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(GeneralGoodsModelAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(owner=request.user)
        else:
            return qs


class DriverInline(admin.TabularInline):
    model = JobOffer.driver_requests.through
    verbose_name = 'Driver Request'
    verbose_name_plural = 'Driver Requests'
    readonly_fields = ['email', 'documents_up_to_date', 'jobs_completed', 'rating', 'accept_driver']

    def get_fields(self, request, obj=None):
        return self.readonly_fields

    def email(self, instance):
        return instance.user.email

    def rating(self, instance):
        return instance.user.rating

    def documents_up_to_date(self, instance):
        return instance.user.documents_up_to_date
    documents_up_to_date.boolean = True

    def accept_driver(self, instance):
        return '<a href="%s">Award Driver</a>' % reverse(
            'marketplace:award_job', kwargs={'job_id': instance.joboffer.id, 'driver_id': instance.user.id})
    accept_driver.allow_tags = True

    def jobs_completed(self, instance):
        return instance.user.jobs_completed

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class JobOfferModelAdmin(admin.ModelAdmin):
    list_filter = ['status', 'job_type', 'vehicle_type']
    list_display = ['id', 'pickup_address', 'destination', 'pickup_datetime', 'status']
    form = AvailableJobOfferAdminForm
    inlines = [DriverInline]
    readonly_fields = ['driver', 'owner_rating']

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            result = PaymentSetting.charge_user(request.user, PaymentSetting.OFFERS, obj.fare)
            if result.get('state', None) == 'approved':
                Transaction.objects.create(user=request.user, amount=obj.fare)
            else:
                messages.add_message(request, messages.ERROR, 'Per-posting charge failed')
                return HttpResponseRedirect(reverse('admin:index'))

        obj.owner = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(JobOfferModelAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(owner=request.user)
        else:
            return qs


admin.site.register(CarModel, CarModelModelAdmin)
admin.site.register(CarMake)
admin.site.register(Car, CarModelAdmin)
admin.site.register(GeneralGood, GeneralGoodsModelAdmin)
admin.site.register(JobOffer, JobOfferModelAdmin)
admin.site.register(CarColor)

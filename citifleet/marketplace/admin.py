from django.contrib import admin
from django.core.urlresolvers import reverse

from .models import CarModel, CarMake, Car, GeneralGood, GoodPhoto, CarPhoto, JobOffer, CarColor
from .forms import AvailableJobOfferAdminForm


class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    min_num = 1
    max_num = 1
    extra = 1


class CarModelModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'make']
    list_filter = ['make']


class CarModelAdmin(admin.ModelAdmin):
    list_display = ['model', 'make', 'type', 'year', 'fuel', 'seats', 'price', 'owner']
    list_filter = ['make', 'model', 'type', 'fuel', 'seats']
    inlines = [CarPhotoInline]
    search_fields = ['owner__email', 'owner__full_name', 'owner__phone']


class GoodPhotoInline(admin.TabularInline):
    model = GoodPhoto
    min_num = 1
    max_num = 1
    extra = 1


class GeneralGoodsModelAdmin(admin.ModelAdmin):
    inlines = [GoodPhotoInline]
    list_display = ['item', 'price', 'condition', 'owner', 'created']
    list_filter = ['condition']
    search_fields = ['owner__email', 'owner__full_name', 'owner__phone']


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
    list_display = ['id', 'owner', 'pickup_address', 'destination', 'pickup_datetime',
                    'status', 'job_type', 'fare', 'gratuity']
    form = AvailableJobOfferAdminForm
    inlines = [DriverInline]
    readonly_fields = ['driver', 'owner_rating']
    search_fields = ['owner__email', 'owner__full_name', 'owner__phone']

    def save_model(self, request, obj, form, change):
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

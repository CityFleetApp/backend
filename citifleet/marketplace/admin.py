from django.contrib import admin

from .models import CarModel, CarMake, Car, GeneralGood, GoodPhoto, CarPhoto, JobOffer
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
    list_display = ['model', 'make', 'type', 'year', 'fuel', 'seats', 'price']
    list_filter = ['make', 'model', 'type', 'fuel', 'seats']
    inlines = [CarPhotoInline]


class GoodPhotoInline(admin.TabularInline):
    model = GoodPhoto
    min_num = 1
    max_num = 1
    extra = 1


class GeneralGoodsModelAdmin(admin.ModelAdmin):
    inlines = [GoodPhotoInline]


class DriverInline(admin.TabularInline):
    model = JobOffer.driver_requests.through
    verbose_name = 'Driver Request'
    verbose_name_plural = 'Driver Requests'
    readonly_fields = ['email', 'documents_up_to_date', 'jobs_completed', 'rating']

    def get_fields(self, request, obj=None):
        return self.readonly_fields

    def email(self, instance):
        return instance.user.email

    def rating(self, instance):
        return instance.user.rating

    def documents_up_to_date(self, instance):
        return instance.user.documents_up_to_date
    documents_up_to_date.boolean = True

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

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(JobOfferModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(owner=request.user)
        else:
            return qs.filter


admin.site.register(CarModel, CarModelModelAdmin)
admin.site.register(CarMake)
admin.site.register(Car, CarModelAdmin)
admin.site.register(GeneralGood, GeneralGoodsModelAdmin)
admin.site.register(JobOffer, JobOfferModelAdmin)

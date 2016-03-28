from django.contrib import admin

from .models import CarModel, CarMake, Car, GeneralGood, GoodPhoto, CarPhoto


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


admin.site.register(CarModel, CarModelModelAdmin)
admin.site.register(CarMake)
admin.site.register(Car, CarModelAdmin)
admin.site.register(GeneralGood, GeneralGoodsModelAdmin)

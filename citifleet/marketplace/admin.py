from django.contrib import admin

from .models import CarModel, CarMake, Car


class CarModelModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'make']
    list_filter = ['make']


class CarModelAdmin(admin.ModelAdmin):
    list_display = ['model', 'make', 'type', 'year', 'fuel', 'seats', 'price']
    list_filter = ['make', 'model', 'type', 'fuel', 'seats']


admin.site.register(CarModel, CarModelModelAdmin)
admin.site.register(CarMake)
admin.site.register(Car, CarModelAdmin)

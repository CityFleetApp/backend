from django.contrib import admin

from image_cropping import ImageCroppingMixin

from .models import Benefit


class BenefitModelAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

admin.site.register(Benefit, BenefitModelAdmin)

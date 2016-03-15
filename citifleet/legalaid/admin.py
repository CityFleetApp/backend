from django.contrib import admin

from .models import Accounting, InsuranceBroker, DMVLawyer, TLCLawyer, Location


class LegalAidModelAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'years_of_experience', 'rating', 'address')

admin.site.register(Accounting, LegalAidModelAdmin)
admin.site.register(InsuranceBroker, LegalAidModelAdmin)
admin.site.register(DMVLawyer, LegalAidModelAdmin)
admin.site.register(TLCLawyer, LegalAidModelAdmin)
admin.site.register(Location)

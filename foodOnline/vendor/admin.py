from django.contrib import admin
from vendor.models import OpeningHour, Vendor

# Register your models here.
class VendorAdmin(admin.ModelAdmin):
    list_display=('user','vendor_name','is_approved','created_at')
    list_display_links=('user','vendor_name')
    list_editable = ('is_approved',)

class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('vendor','days','from_hours','to_hours')

admin.site.register(Vendor,VendorAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)
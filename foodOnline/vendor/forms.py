from django import forms

from vendor.models import OpeningHour, Vendor
from accounts.validators import allow_only_images_validator

class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    class Meta:
        model = Vendor
        fields = ['vendor_name','vendor_license',]


class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['days','from_hours','to_hours','is_closed']
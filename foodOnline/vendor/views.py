from django.shortcuts import render, get_object_or_404, redirect
from vendor.forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from vendor.models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
# Create your views here.

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST,request.FILES,instance=user_profile)
        vendor_form = VendorForm(request.POST,request.FILES,instance=vendor)
        if user_form.is_valid() and vendor_form.is_valid():
            user_form.save()
            vendor_form.save()
            messages.success(request,'Settings Updated!')
            return redirect(vprofile)
        else:
            print(user_form.errors)
            print(vendor_form.errors)
    else:
        user_form = UserProfileForm(instance=user_profile)
        vendor_form = VendorForm(instance=vendor)

    # print(vendor_form)
    # print(user_form)
    context = {'vendor_form': vendor_form, 'user_form':user_form,'vendor':vendor,'user_profile':user_profile}
    return render(request,'vendor/vprofile.html',context)
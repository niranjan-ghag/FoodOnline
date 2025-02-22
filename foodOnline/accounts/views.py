from django.http import HttpResponse
from django.shortcuts import render, redirect
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages

from vendor.forms import VendorForm


# Create your views here.

def registerUser(request):
    if request.method == 'POST':
        form= UserForm(request.POST)
        if form.is_valid():
            # Create User using Form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # form.save()

            # Create user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password'] 
            user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role = User.CUSTOMER 
            user.save()
            messages.success(request,'Your Account has been registered Successfully!')
            return redirect('registerUser')
        else:
            print(form.errors)
        
    else:
        form= UserForm()

    context = {'form': form}
    return render(request, 'accounts/registerUser.html',context)

def registerVendor(request):
    
    if request.method == 'POST':
        user_form= UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if user_form.is_valid() and vendor_form.is_valid() :
            # Create User using Form
            password = user_form.cleaned_data['password']
            user = user_form.save(commit=False)
            user.set_password(password)
            user.role = User.VENDOR
            user_form.save()

            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor_form.save()
            messages.success(request,'Your account has been registered Successfully! Please wait for the verification.')

            return redirect('registerVendor')
    else:
        # get request
        user_form= UserForm()
        vendor_form = VendorForm()
    context = {
        'user_form':user_form,
        'vendor_form' : vendor_form
    }
    return render(request, 'accounts/registerVendor.html',context)
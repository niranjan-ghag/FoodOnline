from django.http import HttpResponse
from django.shortcuts import render, redirect
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages, auth

from vendor.forms import VendorForm
from accounts.utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

# Restrict the customer user from accessing vendor page and vise versa 
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

def check_role_customer(user):
    if user.role == 0:
        return True
    else:
        raise PermissionDenied

# Create your views here.

def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are logged in!')
        return redirect('myAccount')
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
    if request.user.is_authenticated:
        messages.warning(request, 'You are logged in!')
        return redirect('myAccount')
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


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are logged in!')
        return redirect('myAccount')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user:
            auth.login(request, user)
            messages.success(request, 'Logged In Successfully!')
            return redirect('myAccount')
        else:
            messages.error(request,'Invalid Credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request,'You are Logged out!')
    return redirect('login')
    # return render(request, 'accounts/logout.html')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirect_url = detectUser(user)
    return redirect(redirect_url)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custdashboard(request):
    return render(request, 'accounts/custdashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendordashboard(request):
    return render(request, 'accounts/vendordashboard.html')
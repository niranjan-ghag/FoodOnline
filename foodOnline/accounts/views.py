from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages, auth

from orders.models import Order
from vendor.forms import VendorForm
from accounts.utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.template.defaultfilters import slugify
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor

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
            
            # Send Verification mail
            email_subject = 'Please activate your Account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, email_subject, email_template)
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
            vendor_name = vendor_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor_form.save()

            # Send Verification mail
            email_subject = 'Please activate your Account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, email_subject, email_template)
            messages.success(request,'Your account has been registered Successfully! Please wait for the verification.')

            return redirect('login')
        else:
            print("user_form-----",list(user_form.errors.values()))
            print("vendor_form-----",list(vendor_form.errors.values()))
    else:
        # get request
        user_form= UserForm()
        vendor_form = VendorForm()
    
    # print("---user_form----",user_form)
    # print("---vendor_form----",vendor_form)

    context = {
        'user_form':user_form,
        'vendor_form' : vendor_form,
    }
    print("-----context-----",context)
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
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]
    
    context = {'orders': orders,'orders_count': orders.count(),'recent_orders': recent_orders}
    return render(request, 'accounts/custdashboard.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendordashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered = True).order_by('-created_at')
    recent_orders = orders[:10]

    # Current month's Revenue
    current_month = datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month = current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']

    #  total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']

    context = {'vendor': vendor, 'orders':orders, 'orders_count': orders.count(),'recent_orders':recent_orders,'total_revenue':total_revenue,'current_month_revenue': current_month_revenue}
    return render(request, 'accounts/vendordashboard.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'User Registered Successfully!')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAcccount')
    

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email.
            email_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, email_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not Exist.')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active=True
            user.save()
            messages.success(request, 'Password reset Successful')
            return redirect('login')
        else:
            messages.error(request, 'Password don not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please Reset your pasword!')
        return redirect('reset_password')
    else:
        messages.error(request, 'This Link is Expired!')
        return redirect('forgot_password')
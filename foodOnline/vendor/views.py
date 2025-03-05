from django.shortcuts import render, get_object_or_404, redirect
from menu.forms import CategoryForm
from menu.models import Category, FoodItem
from vendor.forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from vendor.models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from django.template.defaultfilters import slugify
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

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context ={'categories': categories}

    return render(request,'vendor/menu_builder.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category,pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {'fooditems':fooditems, 'category':category}
    return render(request,'vendor/fooditems_by_category.html', context)

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category Added Successfully')
            return redirect('menu_builder')
    else:
        form = CategoryForm()
    context = {'form': form}
    return render(request, 'vendor/add_category.html',context)

def edit_category(request, pk=None):
    category =get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category Added Successfully')
            return redirect('menu_builder')
    else:
        form = CategoryForm(instance=category)
    context = {'form': form, 'category':category}
    return render(request, 'vendor/edit_category.html',context)


def delete_category(request,pk=None):
    category =get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been Deleted Successfully')
    return redirect('menu_builder')

    
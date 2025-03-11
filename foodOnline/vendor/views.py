from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from vendor.forms import OpeningHourForm, VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from vendor.models import OpeningHour, Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from django.template.defaultfilters import slugify
from django.http import HttpResponse, JsonResponse
# Create your views here.

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

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



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)

            category.save() #here the category id will be generated
            category.slug = slugify(category_name)+'-'+str(category.id)
            category.save()
            form.save()
            messages.success(request, 'Category Added Successfully')
            return redirect('menu_builder')
    else:
        form = CategoryForm()
    context = {'form': form}
    return render(request, 'vendor/add_category.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
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

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request,pk=None):
    category =get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been Deleted Successfully')
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_fooditem(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Food Item Added Successfully')
            return redirect('fooditems_by_category', food_item.category.id)
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {'form':form}
    return render(request, 'vendor/add_fooditem.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_fooditem(request,pk=None):
    food_item =get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food_item)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Food Item Added Successfully')
            return redirect('fooditems_by_category', food_item.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food_item)
    context = {'form': form, 'food_item':food_item}
    return render(request, 'vendor/edit_fooditem.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_fooditem(request,pk=None):
    food_item =get_object_or_404(FoodItem, pk=pk)
    food_item.delete()
    messages.success(request, 'Food Item has been Deleted Successfully')
    return redirect('fooditems_by_category', food_item.category.id)



def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {'form': form, 'opening_hours' : opening_hours}
    return render(request,'vendor/opening_hours.html', context)


def add_opening_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            days = request.POST.get('days')
            from_hours = request.POST.get('from_hours')
            to_hours = request.POST.get('to_hours')
            is_closed = request.POST.get('is_closed')
            
            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), days= days, from_hours=from_hours, to_hours=to_hours,is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id':hour.id,'day':day.get_days_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id':hour.id,'day':day.get_days_display(), 'from_hours': hour.from_hours,'to_hours': hour.to_hours}
                
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': f'{from_hours} - {to_hours} already exists!'}
                return JsonResponse(response)
        else:
            return HttpResponse('Invalid Request')

    return HttpResponse('Added')


def remove_opening_hours(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id':pk})
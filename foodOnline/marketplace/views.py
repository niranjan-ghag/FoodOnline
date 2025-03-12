from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from foodOnline.context_processors import get_cart_amount, get_cart_counter
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.models import OpeningHour, Vendor
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date, datetime
# Create your views here.
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware
from django.views.decorators.cache import never_cache

def marketplace(request):
    vendors= Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {'vendors': vendors,'vendor_count':vendor_count}
    return render(request, 'marketplace/listings.html',context)

@never_cache 
def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('fooditems',queryset=FoodItem.objects.filter(is_available=True)))
    
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('days', '-from_hours')

    # Check Current day's opening hours.
    today = date.today()
    today = today.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, days= today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {'vendor': vendor,'categories': categories,'cart_items':cart_items, 'opening_hours':opening_hours,'current_opening_hours':current_opening_hours}
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                food_item = FoodItem.objects.get(id=food_id)
                # Check if user has already added the food to cart.
                try:
                    check_cart = Cart.objects.get(user=request.user,food_item=food_item)
                    check_cart.quantity +=1
                    check_cart.save()
                    return JsonResponse({'status':'Success','message': 'Qty Increased for food item','cart_counter': get_cart_counter(request),'qty': check_cart.quantity, 'cart_amount':get_cart_amount(request)})
                except:
                    check_cart = Cart.objects.create(user=request.user,food_item=food_item,quantity=1)
                    return JsonResponse({'status':'Success','message': 'New FoodItem added to Cart','cart_counter': get_cart_counter(request),'qty': check_cart.quantity, 'cart_amount':get_cart_amount(request)})
            except:
                return JsonResponse({'status':'Failed','message': 'This Food Does not Exist!'})
        else:

            return JsonResponse({'status':'Failed','message': 'Invalid Request!'})
    else:
        return JsonResponse({'status':'login_required','message': 'Please Login'})


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                food_item = FoodItem.objects.get(id=food_id)
                # Check if user has already added the food to cart.
                try:
                    check_cart = Cart.objects.get(user=request.user,food_item=food_item)
                    if check_cart.quantity >1:
                        # Decrease 
                        check_cart.quantity -=1
                        check_cart.save()
                        return JsonResponse({'status':'Success','message': 'Qty Decreased for food item','cart_counter': get_cart_counter(request),'qty': check_cart.quantity,'cart_amount':get_cart_amount(request)})
                    else:
                        check_cart.delete()
                        check_cart.quantity =0
                        return JsonResponse({'status':'Success','message': 'No Food item left','cart_counter': get_cart_counter(request),'qty': check_cart.quantity, 'cart_amount':get_cart_amount(request)})
                except:
                    return JsonResponse({'status':'Failed','message': 'You do not have this item in your cart','qty':check_cart.quantity})
            except:
                return JsonResponse({'status':'Failed','message': 'This Food Does not Exist!'})
        else:
            return JsonResponse({'status':'Failed','message': 'Invalid Request!'})
    else:
        return JsonResponse({'status':'login_required','message': 'Please Login'})
    
@login_required(login_url='login')
def cart(request):
    cart_items =Cart.objects.filter(user=request.user).order_by('created_at')
    context = {'cart_items':cart_items}
    return render(request, 'marketplace/cart.html',context)

def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.filter(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success','message': 'Cart item Deleted!','cart_counter': get_cart_counter(request),'cart_amount':get_cart_amount(request)})
            except:
                return JsonResponse({'status':'Failed','message': 'Cart Item does not Exists!'})
        else:
            return JsonResponse({'status':'Failed','message': 'Invalid Request!'})
    else:
        return JsonResponse({'status':'login_required','message': 'Please Login'})
    

def search(request):
    address = request.GET['address']
    keyword = request.GET['keyword']

    fetch_vendor_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available =True).values_list('vendor', flat=True)
    # print(fetch_vendor_by_fooditems)

    vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active= True))
    # vendors = Vendor.objects.filter(vendor_name__icontains=keyword, is_approved=True, user__is_active= True)
    vendor_count = vendors.count()
    
    context = {'vendors':vendors, 'vendor_count':vendor_count}
    return render(request, 'marketplace/listings.html',context)



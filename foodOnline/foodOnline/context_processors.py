from marketplace.models import Cart
from menu.models import FoodItem
from vendor.models import Vendor
from django.conf import settings


def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return dict(vendor=vendor)

def get_google_api(request):
    # {'GOOGLE_API_KEY':settings.GOOGLE_API_KEY}
    return {'GOOGLE_API_KEY':settings.GOOGLE_API_KEY}


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    
    return {'cart_count': cart_count}


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    grand_total = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.food_item.id)
            subtotal += (fooditem.price * item.quantity)

        grand_total = subtotal + tax
    
    return {'subtotal': subtotal, 'grand_total': grand_total, 'tax':tax}
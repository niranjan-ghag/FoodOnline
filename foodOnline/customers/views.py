from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from django.contrib import messages
from django.db.models import Prefetch


from menu.models import FoodItem
from orders.models import Order, OrderedFood
import simplejson as json
# Create your views here.

@login_required(login_url='login')
def cprofile(request):
    profile = get_object_or_404(UserProfile,user = request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        user_form = UserInfoForm(request.POST,instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            print(profile_form.cleaned_data['address']) 
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile Updated!')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)



    context = {'profile_form': profile_form, 'user_form': user_form}
    return render(request, 'customers/cprofile.html', context)

def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {'orders': orders}

    return render(request, 'customers/my_orders.html', context)

def order_details(request, order_number):
    try:
        order = Order.objects.get(user=request.user, order_number=order_number, is_ordered = True)
        ordered_food = OrderedFood.objects.filter(order=order)
        if not ordered_food:
            return redirect('customer')
        subtotal =0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        
        tax_data = json.loads(order.tax_data)
        context={'order': order, 'ordered_food': ordered_food, 'tax_data': tax_data, 'subtotal': subtotal}
        return render(request, 'customers/order_details.html', context)
    except:
        return redirect('customer')

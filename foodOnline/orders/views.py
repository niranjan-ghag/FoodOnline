from django.http import HttpResponse
import simplejson as json
from django.shortcuts import render,redirect

from marketplace.models import Cart
from foodOnline.context_processors import get_cart_amount
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
from orders.utils import generate_order_number

import razorpay
from foodOnline.settings import RZP_KEY_ID, RZP_KEY_SECRET

client = razorpay.Client(auth=(RZP_KEY_ID , RZP_KEY_SECRET))



# Create your views here.
def place_order(request):
    cart_items =Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <=0:
        return redirect('marketplace')
    
    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['grand_total']
    tax_data = get_cart_amount(request)['tax_dict']
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pincode = form.cleaned_data['pincode']
            
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method'] #input type name
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()

            # RAZORPAY Payment
            DATA = {"amount": float(order.total)*100,
                    "currency": "INR",
                    "receipt": f"receipt#{order.order_number}",
                    "notes": {
                        "key1": "value3",
                        "key2": "value2"
                        }
                    }
            rzp_order = client.order.create(data=DATA)
            rzp_order_id = rzp_order['id']
            # print("--rzp_order--",rzp_order)
            

            context = {
                'order': order,
                'cart_items' : cart_items,
                'rzp_order_id': rzp_order_id,
                'RZP_KEY_ID': RZP_KEY_ID,
                'rzp_amount': float(order.total)*100
            }
            return render(request,'orders/place_order.html', context)



        else:
            print(form.errors)

    return render(request, 'orders/place_order.html')


def payments(request):
    # Check if request is ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # Store Payment Details in the Payment model
        order_number = request.POST.get('order_number')
        tranaction_id = request.POSt.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            tranaction_id = tranaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()


        # Update the Order Model
        order.payment = payment
        order.is_ordered =True
        order.save()
        # Move the Cart items to Ordered Food Model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food  = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.food_item
            ordered_food.quantity = item.quantity
            ordered_food.quantity = item.food_item.price
            ordered_food.amount = item.food_item.price * item.quantity
            ordered_food.save()

        return HttpResponse('Saved Ordered Food')

        # Send Order Confirmation email to the customer

        # Send Order Recived Email to the Vendor
        
        #  Clear Cart if Payment Is Success
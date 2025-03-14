from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

from marketplace.models import Cart
from foodOnline.context_processors import get_cart_amount
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
from orders.utils import generate_order_number

from foodOnline.settings import RZP_KEY_ID, RZP_KEY_SECRET
from accounts.utils import send_notification

import simplejson as json
import razorpay
client = razorpay.Client(auth=(RZP_KEY_ID , RZP_KEY_SECRET))



# Create your views here.

@login_required(login_url='login')
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

@login_required(login_url='login')
def payments(request):
    # Check if request is ajax or not
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        print("In")
        # Store Payment Details in the Payment model
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
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
            ordered_food.price = item.food_item.price
            ordered_food.amount = item.food_item.price * item.quantity
            ordered_food.save()

        # Send Order Confirmation email to the customer
        mail_subject = 'Thank You for Ordering..'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email
        }
        send_notification(mail_subject, mail_template, context)
        # return HttpResponse('Data Saved and Email Sent')
        # Send Order Recived Email to the Vendor
        mail_subject = 'You have Received a new Order'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        for i  in cart_items:
            if i.food_item.vendor.user.email not in to_emails:
                to_emails.append(i.food_item.vendor.user.email)
        context = {
            'order' : order,
            'to_email': to_emails
        }
        
        send_notification(mail_subject, mail_template, context)
        #  Clear Cart if Payment Is Success
        # cart_items.delete()
        # Return back to Ajax with status SUCCESS OR FAILURE
        response = {'order_number': order_number, 'transaction_id': transaction_id}
        return JsonResponse(response)

    return HttpResponse('Payments View')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal =0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)

        context = {'order': order, 'ordered_food': ordered_food, 'subtotal': subtotal, 'tax_data': tax_data}
        return render(request,'orders/order_complete.html', context)
    except:
        return redirect('home')
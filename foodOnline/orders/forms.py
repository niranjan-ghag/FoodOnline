from django import forms
from orders.models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','phone','pincode','city','state','country','address','email']
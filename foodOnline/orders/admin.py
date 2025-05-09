from django.contrib import admin
from orders.models import Payment, Order, OrderedFood
# Register your models here.

class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields=('order','payment','user','fooditem','quantity','price','amount')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','name','phone','email','total','payment_method','status','is_ordered']
    inlines = [OrderedFoodInline]

class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ['order','user']
    

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood, OrderedFoodAdmin)

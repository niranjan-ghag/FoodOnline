from django.urls import path
from accounts.views import custdashboard
from customers import views


urlpatterns = [
    path('', custdashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_details/<int:order_number>/', views.order_details, name='order_details'),


]
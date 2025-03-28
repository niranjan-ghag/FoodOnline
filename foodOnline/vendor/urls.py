from django.urls import path
from vendor import views
from accounts import views as AccountViews

urlpatterns = [
    path('',AccountViews.vendordashboard, name='vendor'),
    path('profile/',views.vprofile, name='vprofile'),
    path('menu-builder/',views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/',views.fooditems_by_category, name='fooditems_by_category'),

    # Category CRUD
    path('menu-builder/category/add/',views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/',views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/',views.delete_category, name='delete_category'),

    # FoodItem CRUD
    path('menu-builder/fooditem/add/',views.add_fooditem, name='add_fooditem'),
    path('menu-builder/fooditem/edit/<int:pk>/',views.edit_fooditem, name='edit_fooditem'),
    path('menu-builder/fooditem/delete/<int:pk>/',views.delete_fooditem, name='delete_fooditem'),

    # Opening hours
    path('opening_hours/', views.opening_hours, name='opening_hours'),
    path('opening_hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening_hours/remove/<int:pk>', views.remove_opening_hours, name='remove_opening_hours'),

    path('order_details/<int:order_number>/', views.order_details, name='vendor_order_details'),
    
    path('my_orders/', views.my_orders, name='vendor_my_orders'),

    ]
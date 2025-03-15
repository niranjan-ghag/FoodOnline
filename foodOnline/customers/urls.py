from django.urls import path
from accounts.views import custdashboard
from customers import views


urlpatterns = [
    path('', custdashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
]

from django.contrib import admin
from django.urls import path
from center import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('booking/', views.create_booking, name='create_booking'),

    # Customer registration and login
    path('register/', views.register_customer, name='register_customer'),
    path('login/', views.customer_login, name='login'),

    # Email verification
    path(
        'verify-email/<uidb64>/<token>/',
        views.verify_email,
        name='verify_email'
    ),

    # Customer dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]

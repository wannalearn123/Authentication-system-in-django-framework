from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.webapp, name='webapp'),
    path('register/', views.register, name='register'),#register URL     
    path('login/', views.custom_login, name='login'),  # Override default login
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    # path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('', include('django.contrib.auth.urls')),#auth URLs
    path('result/', views.result, name='result'),

]

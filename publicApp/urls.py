# public/urls.py
from django.urls import path
from . import views

app_name = 'publicApp'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('store/', views.store_page, name='store'),

]
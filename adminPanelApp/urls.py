# adminPanelApp/urls.py
from django.urls import path
from . import views

app_name = 'adminPanelApp'

urlpatterns = [
    path('login/', views.admin_login, name='adminLogin'),
    path('control_dashboard/', views.adminDashboard, name='adminDashboard'),
]
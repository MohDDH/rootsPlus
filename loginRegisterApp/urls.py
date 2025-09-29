from django.urls import path
from . import views

app_name = 'loginRegisterApp'

urlpatterns = [
    path('register/<str:role>/', views.registerAccount, name='registerAccount'),
    path('login/<str:role>/', views.loginAccount, name='loginAccount'),
    path('logout/', views.logout, name='logout'),
]
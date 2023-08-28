from django.urls import path,include
from .views import *

urlpatterns = [
  path('',home,name='home'),
  path('login/', custom_login, name='login'),
  path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
  path('set_password/<str:pk>',set_password,name='set_password'),
]
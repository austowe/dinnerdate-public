from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', indexView, name='index'),
    path('picker/', pickerView, name='picker'),
    path('empty/', emptyList, name='empty'),
    path('location/', locationView, name='location'),
    path('join/', joinView, name='join')
]
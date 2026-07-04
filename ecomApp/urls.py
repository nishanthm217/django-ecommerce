from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from ecomApp import views

urlpatterns = [
    path('',views.base,name="basePage"),
    path('detail/<slug:slug>',views.detail, name='detail')
]

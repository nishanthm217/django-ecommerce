from django.urls import path
from .views import product_list
from .views import product_detail

urlpatterns = [
    path('products/', product_list, name='product-list'),
    path('product/<int:id>', product_detail, name='product_detail' )
]
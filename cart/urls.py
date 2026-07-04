from django.http import JsonResponse
from django.urls import path
from .import views
urlpatterns = [
    path('cart_add/',views.add_cart, name="cart_add"),
    path('cart_overview/',views.cart_overview,name="cart-overview"),
    path('cartProduct_delete/',views.cartProduct_delete,name="delete-product"),
    path('cart_update/',views.cart_update,name="cart-update")
]

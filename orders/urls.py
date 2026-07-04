from django.urls import path
from orders import views
urlpatterns = [
    path('addressForm/',views.AddressFormPage),
    path('checkOutpage/',views.checkOutpage,name='checkoutPage'),
    path('placeOrder/',views.placeOrder,name='place-order'),
    path('order-success/',views.orderSuccess,name='order-success'),
    path('order-failed/',views.orderFailed,name='order-failed')
]
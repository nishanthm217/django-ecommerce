from django.shortcuts import render
from django.http import JsonResponse
from .cart import Cart
from django.shortcuts import get_object_or_404
from ecomApp.models import ProductModel
# Create your views here.
#Getting input from front-end----> Receiving the output in the backend.

def add_cart(request):
    cart = Cart(request)
    if request.method=="POST":
        product_id = request.POST.get("product_id")
        product_quantity = request.POST.get("product_quantity")
        print("product ID added to cart: ", product_id)
        print("product quantity for the product:",product_quantity)
        product = get_object_or_404(ProductModel, id=product_id)
        cart.add(product=product, product_qty=product_quantity)
        cart_quantity = Cart.__len__(cart) #Need to send this response to the front-end by using JsonResponse
    return JsonResponse({"qty":cart_quantity})

def cart_overview(request):
    cart = Cart(request)
    return render(request, 'cart/cart-overview.html', {'cart':cart})

def cartProduct_delete(request):
    cart = Cart(request)
    if request.method=="POST":
        product_id = request.POST.get("product_id")
        cart.delete(product_id=product_id)
        cart_qty = cart.__len__()
        cart_total_qty = cart.get_total_price()
        return JsonResponse({'qty':cart_qty,'total_price':cart_total_qty})

def cart_update(request):
    cart = Cart(request)
    if request.method=="POST":
        product_id = request.POST.get('product_id')
        selected_qty = request.POST.get('selected_qty')
        cart.update(product_id=product_id,selected_qty=selected_qty)
        return JsonResponse({"Movie":"completed!"})
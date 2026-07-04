from django.shortcuts import render, redirect
from .forms import AddressForm
from cart.cart import Cart
from django.http import JsonResponse
from .models import orderItem, Order

# Create your views here.
from .models import Address
def AddressFormPage(request):
    try:
        user = request.user
        address = Address.objects.get(user=user)
        
    except Address.DoesNotExist:
        address = None    
        
    form = AddressForm()
    if request.method =="POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('basePage')
    form = AddressForm(instance=address)
    return render(request,'orders/AddressForm.html',{'form':form})  

def checkOutpage(request):
    if request.user.is_authenticated:
        try:
            address = Address.objects.get(user=request.user)
            return render(request,'orders/checkout.html',{'address':address})
        except:
            return render(request,'orders/checkout.html')
        
    return render(request,'orders/checkout.html')

def placeOrder(request):
    if request.method =="POST":
        order_message=False
        cart = Cart(request)
        total_amount = cart.get_total_price()
        if request.user.is_authenticated:
            order = Order.objects.create(user=request.user,total_amount=total_amount)
            for item in cart:
                orderItem.objects.create(product=item['product'],order=order,quantity=item['qty'])
            order_message=True
        else:
            order=Order.objects.create(total_amount=total_amount)
            for item in cart:
                orderItem.objects.create(product=item['product'],order=order,quantity=item['qty'])
            order_message=True
        return JsonResponse({'message':order_message})
    
def orderSuccess(request):
    request.session.pop('cart', None)
    return render(request,'orders/order-success.html')

def orderFailed(request):
    return render(request,'orders/order-failed.html')
from django.shortcuts import render
from ecomApp.models import ProductModel
# Create your views here.

def base(request):
    products = ProductModel.objects.all()
    return render(request,'ecomApp/index.html',{'products':products})

def detail(request,slug):
    product = ProductModel.objects.get(slug=slug)
    return render(request,'ecomApp/detail.html',{'product':product})

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework import status
from ecomApp.models import ProductModel
from .serializers import ProductSerializer

from ecomApp.models import ProductModel

@api_view(['GET','POST'])
def product_list(request):
    if request.method =='GET':
        products = ProductModel.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


@api_view(['GET','PUT','DELETE','PATCH'])
def product_detail(request, id):
    product = get_object_or_404(ProductModel, id=id)
    
    if request.method =="GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    elif request.method =="PATCH":
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    elif request.method =='PUT':
        serializer = ProductSerializer(product,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    elif request.method =='DELETE':
        product.delete()
        return Response({"message":"Product Deleted!"},status = status.HTTP_204_NO_CONTENT)
        
        

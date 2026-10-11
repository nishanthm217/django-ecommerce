from rest_framework import serializers
from ecomApp.models import ProductModel


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductModel
        fields = '__all__'
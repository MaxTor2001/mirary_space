"""Сериализаторы корзины."""
from rest_framework import serializers

from goods.serializers import ProductSerializer

from .models import Cart


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    products_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "product", "thickness", "length", "quantity", "products_price")


class CartWriteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    thickness = serializers.DecimalField(max_digits=4, decimal_places=1, required=False, allow_null=True)
    length = serializers.DecimalField(max_digits=4, decimal_places=1, required=False, allow_null=True)

"""Сериализаторы каталога."""
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(source="products.count", read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "products_count")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    sell_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "description", "material", "size",
            "price", "discount", "sell_price", "quantity", "image", "category",
        )

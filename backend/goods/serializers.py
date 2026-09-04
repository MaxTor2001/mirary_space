"""Сериализаторы каталога."""
from django.conf import settings
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
    image = serializers.SerializerMethodField()

    def get_image(self, product):
        """Адрес картинки для браузера, а не для внутренней сети docker."""
        if not product.image:
            return None
        return settings.PUBLIC_MEDIA_URL + product.image.name

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "description", "material", "size",
            "price", "discount", "sell_price", "quantity", "image", "category",
        )

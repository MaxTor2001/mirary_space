"""Сериализаторы каталога."""
from django.conf import settings
from rest_framework import serializers

from .models import Category, Product


def _media_url(field):
    return settings.PUBLIC_MEDIA_URL + field.name if field else None


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(source="products.count", read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "products_count")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    thread_display = serializers.CharField(source="get_thread_display", read_only=True)
    sell_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    def get_image(self, product):
        """Адрес картинки для браузера, а не для внутренней сети docker."""
        return _media_url(product.image)

    def get_thumbnail(self, product):
        """Уменьшенная версия для каталога; если её нет — отдаём оригинал."""
        return _media_url(product.thumbnail) or _media_url(product.image)

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "description", "material",
            "thicknesses", "lengths", "thread", "thread_display",
            "price", "discount", "sell_price", "quantity", "image", "thumbnail", "category",
        )

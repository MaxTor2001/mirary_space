"""API каталога: список и карточка товара."""
from rest_framework import viewsets

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    pagination_class = None


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer
    lookup_field = "slug"
    filterset_fields = {"category__slug": ["exact"], "price": ["gte", "lte"]}
    search_fields = ("name", "description", "material")
    ordering_fields = ("price", "name", "created_at")

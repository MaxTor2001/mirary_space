"""Сериализаторы заказов."""
from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    products_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "name", "price", "quantity", "products_price")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "first_name", "last_name", "phone", "email", "delivery_address",
            "requires_delivery", "payment_on_get", "is_paid", "status", "status_display",
            "created_at", "items", "total_price",
        )
        read_only_fields = ("is_paid", "status", "created_at")

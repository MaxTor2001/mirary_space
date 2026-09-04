"""API заказов: создание из корзины и история покупок."""
from django.db import transaction
from rest_framework import mixins, permissions, serializers, viewsets

from carts.services import cart_items

from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    @transaction.atomic
    def perform_create(self, serializer):
        """Создаёт заказ из корзины, списывает остатки и очищает корзину."""
        items = cart_items(self.request)
        if not items.exists():
            raise serializers.ValidationError("Корзина пуста")

        order = serializer.save(user=self.request.user)
        for item in items:
            product = item.product
            if item.quantity > product.quantity:
                raise serializers.ValidationError(
                    f"Недостаточно товара «{product.name}» на складе: осталось {product.quantity}"
                )
            product.quantity -= item.quantity
            product.save(update_fields=["quantity"])
            OrderItem.objects.create(
                order=order,
                product=product,
                name=product.name,
                price=product.sell_price,
                quantity=item.quantity,
            )
        items.delete()

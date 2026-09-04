"""API корзины: просмотр, добавление, изменение и слияние после входа."""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from goods.models import Product

from .models import Cart
from .serializers import CartSerializer, CartWriteSerializer
from .services import cart_items, cart_owner, chosen_size


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    pagination_class = None
    http_method_names = ("get", "post", "patch", "delete")

    def get_queryset(self):
        return cart_items(self.request)

    def list(self, request, *args, **kwargs):
        items = self.get_queryset()
        return Response(
            {
                "items": CartSerializer(items, many=True).data,
                "total_quantity": items.total_quantity(),
                "total_price": items.total_price(),
            }
        )

    def create(self, request, *args, **kwargs):
        """Добавляет товар в корзину или увеличивает количество существующей позиции."""
        payload = CartWriteSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        product = get_object_or_404(Product, pk=payload.validated_data["product_id"])
        thickness = chosen_size(
            payload.validated_data.get("thickness"), product.thicknesses, "thickness"
        )
        length = chosen_size(payload.validated_data.get("length"), product.lengths, "length")

        item, created = Cart.objects.get_or_create(
            product=product, thickness=thickness, length=length,
            defaults={"quantity": 0}, **cart_owner(request)
        )
        item.quantity += payload.validated_data["quantity"]
        item.save(update_fields=["quantity"])
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(CartSerializer(item).data, status=code)

    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        quantity = int(request.data.get("quantity", item.quantity))
        if quantity < 1:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        item.quantity = quantity
        item.save(update_fields=["quantity"])
        return Response(CartSerializer(item).data)

    @action(detail=False, methods=["post"])
    def clear(self, request):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def merge(self, request):
        """Переносит анонимную корзину пользователю после входа."""
        session_key = request.data.get("session_key", "")
        if not request.user.is_authenticated or not session_key:
            return Response({"detail": "Нужен вход и ключ сессии"}, status=status.HTTP_400_BAD_REQUEST)

        for guest_item in Cart.objects.filter(user__isnull=True, session_key=session_key):
            item, _ = Cart.objects.get_or_create(
                user=request.user, product=guest_item.product,
                thickness=guest_item.thickness, length=guest_item.length,
                defaults={"quantity": 0},
            )
            item.quantity += guest_item.quantity
            item.save(update_fields=["quantity"])
            guest_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

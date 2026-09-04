"""Корзина покупателя: авторизованного или анонимного."""
from django.conf import settings
from django.db import models

from goods.models import Product


class CartQuerySet(models.QuerySet):
    def total_price(self):
        return sum(item.products_price for item in self)

    def total_quantity(self):
        return sum(item.quantity for item in self)


class Cart(models.Model):
    """Позиция корзины: товар и его количество."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
        blank=True,
        null=True,
        verbose_name="Пользователь",
    )
    session_key = models.CharField("Ключ сессии", max_length=64, blank=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items", verbose_name="Товар"
    )
    thickness = models.DecimalField("Толщина, мм", max_digits=4, decimal_places=1, null=True, blank=True)
    length = models.DecimalField("Длина, мм", max_digits=4, decimal_places=1, null=True, blank=True)
    quantity = models.PositiveIntegerField("Количество", default=1)
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)

    objects = CartQuerySet.as_manager()

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        ordering = ("created_at",)
        constraints = [
            # nulls_distinct=False: позиции без размеров тоже должны склеиваться в одну.
            models.UniqueConstraint(
                fields=("user", "product", "thickness", "length"), name="unique_user_product",
                condition=models.Q(user__isnull=False), nulls_distinct=False,
            ),
            models.UniqueConstraint(
                fields=("session_key", "product", "thickness", "length"), name="unique_session_product",
                condition=models.Q(user__isnull=True), nulls_distinct=False,
            ),
        ]

    def __str__(self):
        owner = self.user.username if self.user else f"аноним {self.session_key[:8]}"
        return f"{owner}: {self.product.name} x{self.quantity}"

    @property
    def products_price(self):
        return round(self.product.sell_price * self.quantity, 2)

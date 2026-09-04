"""Заказы магазина и их позиции."""
from django.conf import settings
from django.db import models

from goods.models import Product


class Order(models.Model):
    """Оформленный заказ покупателя."""

    STATUS_CHOICES = [
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("shipped", "Отправлен"),
        ("done", "Выполнен"),
        ("canceled", "Отменён"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
        verbose_name="Пользователь",
    )
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    phone = models.CharField("Телефон", max_length=32)
    email = models.EmailField("Email", blank=True)
    delivery_address = models.TextField("Адрес доставки", blank=True)
    requires_delivery = models.BooleanField("Нужна доставка", default=True)
    payment_on_get = models.BooleanField("Оплата при получении", default=True)
    is_paid = models.BooleanField("Оплачен", default=False)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Заказ №{self.pk} от {self.first_name} {self.last_name}"

    @property
    def total_price(self):
        return sum(item.products_price for item in self.items.all())


class OrderItem(models.Model):
    """Позиция заказа с зафиксированными названием и ценой."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, verbose_name="Товар"
    )
    name = models.CharField("Название", max_length=200)
    thickness = models.DecimalField("Толщина, мм", max_digits=4, decimal_places=1, null=True, blank=True)
    length = models.DecimalField("Длина, мм", max_digits=4, decimal_places=1, null=True, blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    @property
    def products_price(self):
        return round(self.price * self.quantity, 2)

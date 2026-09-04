"""Онлайн-платежи заказов через ЮKassa."""
from django.db import models

from orders.models import Order


class Payment(models.Model):
    """Платёж в ЮKassa: сумма, статус и адрес формы оплаты."""

    STATUS_CHOICES = [
        ("pending", "Ожидает оплаты"),
        ("waiting_for_capture", "Ожидает подтверждения"),
        ("succeeded", "Оплачен"),
        ("canceled", "Отменён"),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="payments", verbose_name="Заказ"
    )
    external_id = models.CharField("Идентификатор в ЮKassa", max_length=64, unique=True)
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=32, choices=STATUS_CHOICES, default="pending")
    confirmation_url = models.URLField("Ссылка на оплату", max_length=500, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Платёж {self.amount} ₽ по заказу №{self.order_id}: {self.get_status_display()}"

"""Каталог: категории и товары для пирсинга."""
from decimal import Decimal

from django.db import models


class Category(models.Model):
    """Категория каталога, например «Серьги для носа»."""

    name = models.CharField("Название", max_length=150)
    slug = models.SlugField("URL", max_length=200, unique=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар каталога с ценой, скидкой и остатком на складе."""

    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("URL", max_length=250, unique=True)
    description = models.TextField("Описание", blank=True)
    material = models.CharField("Материал", max_length=100, blank=True)
    size = models.CharField("Размер", max_length=50, blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    discount = models.DecimalField("Скидка, %", max_digits=5, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField("Остаток", default=0)
    image = models.ImageField("Изображение", upload_to="goods/", blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория"
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def sell_price(self) -> Decimal:
        """Цена с учётом скидки, округлённая до копеек."""
        if not self.discount:
            return self.price
        return round(self.price * (1 - self.discount / 100), 2)

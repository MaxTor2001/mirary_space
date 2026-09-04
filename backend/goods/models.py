"""Каталог: категории и товары для пирсинга."""
from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.db import models
from slugify import slugify

from .images import FULL_SIDE, THUMB_SIDE, basename, encode, thumb_filename


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

    THREADS = [
        ("internal", "Внутренняя резьба"),
        ("external", "Внешняя резьба"),
        ("threadless", "Безрезьбовое (push-in)"),
    ]

    name = models.CharField("Название", max_length=200)
    slug = models.SlugField(
        "URL", max_length=250, unique=True, blank=True,
        help_text="Пустое поле — адрес соберётся из названия автоматически.",
    )
    description = models.TextField("Описание", blank=True)
    material = models.CharField("Материал", max_length=100, blank=True)
    thicknesses = ArrayField(
        models.DecimalField(max_digits=4, decimal_places=1),
        verbose_name="Толщина, мм", blank=True, default=list,
        help_text="Несколько значений — через запятую: 1.2, 1.6",
    )
    lengths = ArrayField(
        models.DecimalField(max_digits=4, decimal_places=1),
        verbose_name="Длина, мм", blank=True, default=list,
        help_text="Несколько значений — через запятую: 6, 8, 10",
    )
    thread = models.CharField("Тип резьбы", max_length=20, choices=THREADS, blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    discount = models.DecimalField("Скидка, %", max_digits=5, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField("Остаток", default=0)
    image = models.ImageField("Изображение", upload_to="goods/", blank=True, null=True)
    thumbnail = models.ImageField("Миниатюра", upload_to="goods/thumbs/", blank=True, editable=False)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Имя картинки на момент загрузки из базы: по нему видно, что при
        # замене фото прежний файл надо удалить — сам Django его не трогает.
        self._loaded_image = self.image.name

    def save(self, *args, **kwargs):
        """После сохранения ужимает загруженный оригинал и обновляет миниатюру."""
        if not self.slug:
            self.slug = self._build_slug()
        super().save(*args, **kwargs)

        if self._loaded_image and self._loaded_image != self.image.name:
            self.image.storage.delete(self._loaded_image)
            self._loaded_image = self.image.name

        if not self.image:
            return

        wanted = thumb_filename(self.image.name)
        if basename(self.thumbnail.name) == wanted:
            return

        self.image.open("rb")
        original = self.image.read()

        # Старые файлы удаляются, иначе хранилище выдаст новое имя с суффиксом,
        # а прежний многомегабайтный оригинал останется лежать на диске.
        image_file = basename(self.image.name)
        self.image.storage.delete(self.image.name)
        if self.thumbnail:
            self.thumbnail.storage.delete(self.thumbnail.name)

        self.image.save(image_file, encode(original, FULL_SIDE), save=False)
        self.thumbnail.save(wanted, encode(original, THUMB_SIDE), save=False)
        super().save(update_fields=["image", "thumbnail"])
        self._loaded_image = self.image.name

    def _build_slug(self) -> str:
        """Адрес из названия; при совпадении добавляет числовой суффикс."""
        base = slugify(self.name)[:240] or "tovar"
        slug = base
        number = 2
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base}-{number}"
            number += 1
        return slug

    @property
    def sell_price(self) -> Decimal:
        """Цена с учётом скидки, округлённая до копеек."""
        if not self.discount:
            return self.price
        return round(self.price * (1 - self.discount / 100), 2)

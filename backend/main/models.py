"""Контент главной страницы."""
from django.db import models


class Banner(models.Model):
    """Промо-баннер на главной странице."""

    title = models.CharField("Заголовок", max_length=150)
    subtitle = models.CharField("Подзаголовок", max_length=250, blank=True)
    link = models.CharField("Ссылка", max_length=250, blank=True)
    image = models.ImageField("Изображение", upload_to="banners/", blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)
    sort = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ("sort",)

    def __str__(self):
        return self.title

"""Модель пользователя магазина Mirari."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь с контактами для доставки заказа."""

    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    image = models.ImageField("Аватар", upload_to="users/", blank=True, null=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

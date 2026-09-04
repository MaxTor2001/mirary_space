"""Общая логика доступа к корзине по пользователю или ключу сессии."""
from rest_framework.serializers import ValidationError

from .models import Cart


def chosen_size(value, available, label):
    """Проверяет выбранный размер: он обязателен, если у товара есть варианты."""
    if not available:
        return None
    if value not in available:
        variants = ", ".join(f"{v:g}" for v in available)
        raise ValidationError({label: f"Выберите значение из списка: {variants} мм"})
    return value


def cart_owner(request) -> dict:
    """Фильтр владельца корзины: пользователь или анонимный ключ сессии."""
    if request.user.is_authenticated:
        return {"user": request.user}
    return {"user": None, "session_key": request.headers.get("X-Cart-Session", "")}


def cart_items(request):
    return Cart.objects.filter(**cart_owner(request)).select_related("product", "product__category")

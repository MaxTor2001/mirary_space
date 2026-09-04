"""Общая логика доступа к корзине по пользователю или ключу сессии."""
from .models import Cart


def cart_owner(request) -> dict:
    """Фильтр владельца корзины: пользователь или анонимный ключ сессии."""
    if request.user.is_authenticated:
        return {"user": request.user}
    return {"user": None, "session_key": request.headers.get("X-Cart-Session", "")}


def cart_items(request):
    return Cart.objects.filter(**cart_owner(request)).select_related("product", "product__category")

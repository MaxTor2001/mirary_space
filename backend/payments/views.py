"""API онлайн-оплаты: создание платежа, возврат покупателя и уведомления ЮKassa."""
import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from yookassa.domain.exceptions import ApiError

from orders.models import Order

from . import services
from .models import Payment
from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)


def refused(error: ApiError) -> Response:
    """Ответ витрине, когда ЮKassa не приняла запрос: ключи, чек, сумма."""
    logger.warning("ЮKassa отклонила запрос: %s", error.content)
    description = (error.content or {}).get("description", "сервис оплаты недоступен")
    return Response({"detail": f"ЮKassa: {description}"}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
def availability(request):
    """Витрина спрашивает, предлагать ли оплату онлайн."""
    return Response({"enabled": services.enabled()})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create(request):
    """Создаёт платёж по заказу и возвращает ссылку на форму оплаты ЮKassa."""
    if not services.enabled():
        return Response({"detail": "Онлайн-оплата не подключена"}, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, pk=request.data.get("order"), user=request.user)
    if order.is_paid:
        return Response({"detail": "Заказ уже оплачен"}, status=status.HTTP_400_BAD_REQUEST)

    payment = order.payments.filter(status="pending").exclude(confirmation_url="").first()
    if payment is None:
        try:
            payment = services.create(order)
        except ApiError as error:
            return refused(error)
    return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync(request):
    """Перечитывает статус платежа: покупатель вернулся с формы оплаты."""
    order = get_object_or_404(Order, pk=request.data.get("order"), user=request.user)
    payment = order.payments.first()
    if payment is None:
        return Response({"detail": "Платежей по заказу нет"}, status=status.HTTP_404_NOT_FOUND)
    try:
        return Response(PaymentSerializer(services.sync(payment)).data)
    except ApiError as error:
        return refused(error)


@api_view(["POST"])
def webhook(request):
    """Уведомление ЮKassa: статус берём не из тела запроса, а перечитыванием платежа.

    Ошибку перечитывания не глушим: ЮKassa повторит уведомление, получив не 2xx.
    """
    external_id = (request.data.get("object") or {}).get("id")
    payment = Payment.objects.filter(external_id=external_id).first()
    if payment is not None:
        services.sync(payment)
    return Response(status=status.HTTP_200_OK)

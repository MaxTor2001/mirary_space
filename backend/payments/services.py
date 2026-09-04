"""Обмен с API ЮKassa: создание платежа и проверка его статуса."""
from django.conf import settings
from yookassa import Configuration
from yookassa import Payment as YooPayment

from .models import Payment


def enabled() -> bool:
    """Онлайн-оплата доступна, только когда в окружении заданы ключи магазина."""
    return bool(settings.YOOKASSA_SHOP_ID and settings.YOOKASSA_SECRET_KEY)


def configure():
    Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)


def item_description(item) -> str:
    """Название позиции для чека: товар и выбранные размеры, не длиннее 128 символов."""
    sizes = " × ".join(f"{float(size):g}" for size in (item.thickness, item.length) if size)
    name = f"{item.name} ({sizes} мм)" if sizes else item.name
    return name[:128]


def receipt(order) -> dict:
    """Данные чека по 54-ФЗ: контакт покупателя и позиции заказа."""
    customer = {"email": order.email} if order.email else {"phone": order.phone}
    data = {
        "customer": customer,
        "items": [
            {
                "description": item_description(item),
                "quantity": str(item.quantity),
                "amount": {"value": f"{item.price:.2f}", "currency": "RUB"},
                "vat_code": settings.YOOKASSA_VAT_CODE,
                "payment_subject": "commodity",
                "payment_mode": "full_payment",
            }
            for item in order.items.all()
        ],
    }
    if settings.YOOKASSA_TAX_SYSTEM_CODE:
        data["tax_system_code"] = settings.YOOKASSA_TAX_SYSTEM_CODE
    return data


def create(order) -> Payment:
    """Создаёт платёж в ЮKassa и сохраняет его вместе со ссылкой на форму оплаты."""
    configure()
    request = {
        "amount": {"value": f"{order.total_price:.2f}", "currency": "RUB"},
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": f"{settings.SITE_URL}/orders/{order.pk}",
        },
        "description": f"Заказ №{order.pk} в интернет-магазине Mirari",
        "metadata": {"order_id": str(order.pk)},
    }
    if settings.YOOKASSA_SEND_RECEIPT:
        request["receipt"] = receipt(order)

    # Ключ идемпотентности привязан к заказу и сумме: повторный запрос
    # не создаст второй платёж, а вернёт уже созданный.
    remote = YooPayment.create(request, f"order-{order.pk}-{order.total_price}")
    return Payment.objects.create(
        order=order,
        external_id=remote.id,
        amount=order.total_price,
        status=remote.status,
        confirmation_url=remote.confirmation.confirmation_url if remote.confirmation else "",
    )


def sync(payment: Payment) -> Payment:
    """Перечитывает платёж в ЮKassa и переносит его статус в заказ."""
    configure()
    remote = YooPayment.find_one(payment.external_id)
    payment.status = remote.status
    payment.save(update_fields=["status", "updated_at"])

    order = payment.order
    if remote.status == "succeeded" and not order.is_paid:
        order.is_paid = True
        order.status = "processing"
        order.save(update_fields=["is_paid", "status"])
    return payment

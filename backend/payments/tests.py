"""Проверки онлайн-оплаты: запрос в ЮKassa, уведомление и синхронизация статуса."""
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from yookassa.domain.exceptions import UnauthorizedError

from goods.models import Category, Product
from orders.models import Order, OrderItem

from .models import Payment

KEYS = {"YOOKASSA_SHOP_ID": "123456", "YOOKASSA_SECRET_KEY": "test_secret", "SITE_URL": "https://mirari.space"}


def remote_payment(status="pending"):
    """Ответ ЮKassa на создание платежа."""
    return SimpleNamespace(
        id="2f0c1a00-000f-5000-9000-1f2c3d4e5f60",
        status=status,
        confirmation=SimpleNamespace(confirmation_url="https://yoomoney.ru/checkout/payments/v2/contract"),
    )


@override_settings(**KEYS)
class PaymentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="buyer", email="buyer@example.com", password="secret")
        category = Category.objects.create(name="Лабреты", slug="labrets")
        self.product = Product.objects.create(name="Лабрет", price=1000, quantity=5, category=category)
        self.order = Order.objects.create(
            user=self.user, first_name="Аня", last_name="Иванова",
            phone="+79990000000", email="buyer@example.com", payment_on_get=False,
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, name="Лабрет",
            thickness="1.2", length="8.0", price=1000, quantity=2,
        )
        self.client.force_login(self.user)

    def test_enabled_flag_follows_keys(self):
        self.assertTrue(self.client.get(reverse("payment-enabled")).json()["enabled"])
        with override_settings(YOOKASSA_SHOP_ID=""):
            self.assertFalse(self.client.get(reverse("payment-enabled")).json()["enabled"])

    def test_create_sends_receipt_and_saves_payment(self):
        with patch("payments.services.YooPayment.create", return_value=remote_payment()) as create:
            response = self.client.post(
                reverse("payment-create"), {"order": self.order.pk}, content_type="application/json"
            )

        self.assertEqual(response.status_code, 201)
        request = create.call_args.args[0]
        self.assertEqual(request["amount"], {"value": "2000.00", "currency": "RUB"})
        self.assertEqual(request["confirmation"]["return_url"], f"https://mirari.space/orders/{self.order.pk}")
        self.assertEqual(request["receipt"]["customer"], {"email": "buyer@example.com"})
        item = request["receipt"]["items"][0]
        self.assertEqual(item["description"], "Лабрет (1.2 × 8 мм)")
        self.assertEqual(item["amount"], {"value": "1000.00", "currency": "RUB"})
        self.assertEqual(item["quantity"], "2")

        payment = Payment.objects.get()
        self.assertEqual(payment.status, "pending")
        self.assertEqual(response.json()["confirmation_url"], payment.confirmation_url)

    def test_create_reuses_pending_payment(self):
        with patch("payments.services.YooPayment.create", return_value=remote_payment()):
            self.client.post(reverse("payment-create"), {"order": self.order.pk}, content_type="application/json")
            self.client.post(reverse("payment-create"), {"order": self.order.pk}, content_type="application/json")
        self.assertEqual(Payment.objects.count(), 1)

    def test_webhook_marks_order_paid_after_check_in_api(self):
        payment = Payment.objects.create(
            order=self.order, external_id=remote_payment().id, amount=2000, confirmation_url="https://pay"
        )
        with patch("payments.services.YooPayment.find_one", return_value=remote_payment("succeeded")):
            response = self.client.post(
                reverse("payment-webhook"),
                {"event": "payment.succeeded", "object": {"id": payment.external_id}},
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(payment.status, "succeeded")
        self.assertTrue(self.order.is_paid)
        self.assertEqual(self.order.status, "processing")

    def test_webhook_ignores_unknown_payment(self):
        with patch("payments.services.YooPayment.find_one") as find_one:
            response = self.client.post(
                reverse("payment-webhook"),
                {"event": "payment.succeeded", "object": {"id": "unknown"}},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        find_one.assert_not_called()

    def test_sync_updates_status_for_owner_only(self):
        payment = Payment.objects.create(
            order=self.order, external_id=remote_payment().id, amount=2000, confirmation_url="https://pay"
        )
        with patch("payments.services.YooPayment.find_one", return_value=remote_payment("canceled")):
            response = self.client.post(
                reverse("payment-sync"), {"order": self.order.pk}, content_type="application/json"
            )
        self.assertEqual(response.json()["status"], "canceled")
        payment.refresh_from_db()
        self.assertEqual(payment.status, "canceled")

        stranger = get_user_model().objects.create_user(username="stranger", email="stranger@example.com", password="secret")
        self.client.force_login(stranger)
        response = self.client.post(
            reverse("payment-sync"), {"order": self.order.pk}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_create_reports_yookassa_refusal(self):
        error = UnauthorizedError({"description": "Error in shopId or secret key", "code": "invalid_credentials"})
        with patch("payments.services.YooPayment.create", side_effect=error):
            response = self.client.post(
                reverse("payment-create"), {"order": self.order.pk}, content_type="application/json"
            )
        self.assertEqual(response.status_code, 502)
        self.assertIn("Error in shopId", response.json()["detail"])
        self.assertFalse(Payment.objects.exists())

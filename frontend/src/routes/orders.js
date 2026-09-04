/** Оформление заказа, оплата и история покупок. */
import { Router } from "express";

import { api, ApiError } from "../api.js";

const router = Router();

/** Заказы доступны только авторизованным покупателям. */
function requireAuth(req, res, next) {
  if (!req.session.user) {
    req.session.flash = { type: "error", text: "Войдите, чтобы оформить заказ" };
    return res.redirect("/login");
  }
  next();
}

/** Предлагаем оплату онлайн, только если бэкенду выданы ключи ЮKassa. */
async function onlinePaymentEnabled(session) {
  const { enabled } = await api("/payments/enabled/", { session });
  return enabled;
}

/** Создаёт платёж и уводит покупателя на форму оплаты ЮKassa. */
async function startPayment(req, res, orderId) {
  try {
    const payment = await api("/payments/", {
      method: "POST",
      session: req.session,
      body: { order: orderId },
    });
    return res.redirect(payment.confirmation_url);
  } catch (error) {
    if (!(error instanceof ApiError)) throw error;
    req.session.flash = {
      type: "error",
      text: `Не удалось перейти к оплате: ${error.message}. Заказ сохранён, оплату можно повторить.`,
    };
    return res.redirect(`/orders/${orderId}`);
  }
}

router.get("/", requireAuth, async (req, res) => {
  const orders = await api("/orders/", { session: req.session });
  res.render("orders", { title: "Мои заказы", orders });
});

router.get("/checkout", requireAuth, async (req, res) => {
  const cart = await api("/carts/", { session: req.session });
  if (!cart.items.length) {
    req.session.flash = { type: "error", text: "Корзина пуста" };
    return res.redirect("/cart");
  }
  res.render("checkout", {
    title: "Оформление заказа",
    cart,
    form: {},
    error: null,
    onlinePayment: await onlinePaymentEnabled(req.session),
  });
});

router.post("/checkout", requireAuth, async (req, res) => {
  const form = req.body;
  const payOnline = form.payment_method === "online";
  try {
    const order = await api("/orders/", {
      method: "POST",
      session: req.session,
      body: {
        first_name: form.first_name,
        last_name: form.last_name,
        phone: form.phone,
        email: form.email,
        delivery_address: form.delivery_address,
        requires_delivery: form.requires_delivery === "on",
        payment_on_get: !payOnline,
      },
    });
    if (payOnline) return startPayment(req, res, order.id);
    req.session.flash = { type: "success", text: `Заказ №${order.id} принят` };
    res.redirect("/orders");
  } catch (error) {
    if (!(error instanceof ApiError) || error.status >= 500) throw error;
    const cart = await api("/carts/", { session: req.session });
    res.status(400).render("checkout", {
      title: "Оформление заказа",
      cart,
      form,
      error: error.message,
      onlinePayment: await onlinePaymentEnabled(req.session),
    });
  }
});

router.post("/:id/pay", requireAuth, async (req, res) => startPayment(req, res, req.params.id));

router.get("/:id", requireAuth, async (req, res) => {
  let order = await api(`/orders/${req.params.id}/`, { session: req.session });
  // Покупатель вернулся с формы оплаты: уведомление ЮKassa могло ещё не дойти,
  // поэтому статус платежа перечитываем сами.
  if (!order.is_paid && !order.payment_on_get) {
    const synced = await api("/payments/sync/", {
      method: "POST",
      session: req.session,
      body: { order: order.id },
    }).catch(() => null);
    if (synced?.status === "succeeded") order = await api(`/orders/${order.id}/`, { session: req.session });
  }
  res.render("order", { title: `Заказ №${order.id}`, order });
});

export default router;

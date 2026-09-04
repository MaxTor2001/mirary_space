/** Оформление заказа и история покупок. */
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
  res.render("checkout", { title: "Оформление заказа", cart, form: {}, error: null });
});

router.post("/checkout", requireAuth, async (req, res) => {
  const form = req.body;
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
        payment_on_get: form.payment_on_get === "on",
      },
    });
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
    });
  }
});

router.get("/:id", requireAuth, async (req, res) => {
  const order = await api(`/orders/${req.params.id}/`, { session: req.session });
  res.render("order", { title: `Заказ №${order.id}`, order });
});

export default router;

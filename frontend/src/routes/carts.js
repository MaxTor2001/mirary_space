/** Корзина покупателя. */
import { Router } from "express";

import { api } from "../api.js";

const router = Router();

router.get("/", async (req, res) => {
  const cart = await api("/carts/", { session: req.session });
  res.render("cart", { title: "Корзина", cart });
});

router.post("/add", async (req, res) => {
  await api("/carts/", {
    method: "POST",
    session: req.session,
    body: { product_id: Number(req.body.product_id), quantity: Number(req.body.quantity || 1) },
  });
  req.session.flash = { type: "success", text: "Товар добавлен в корзину" };
  res.redirect(req.body.next || "/cart");
});

router.post("/update/:id", async (req, res) => {
  await api(`/carts/${req.params.id}/`, {
    method: "PATCH",
    session: req.session,
    body: { quantity: Number(req.body.quantity) },
  });
  res.redirect("/cart");
});

router.post("/remove/:id", async (req, res) => {
  await api(`/carts/${req.params.id}/`, { method: "DELETE", session: req.session });
  res.redirect("/cart");
});

router.post("/clear", async (req, res) => {
  await api("/carts/clear/", { method: "POST", session: req.session });
  res.redirect("/cart");
});

export default router;

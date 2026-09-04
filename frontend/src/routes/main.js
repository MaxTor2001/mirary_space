/** Главная страница и информационные разделы. */
import { Router } from "express";

import { api } from "../api.js";

const router = Router();

router.get("/", async (req, res) => {
  const data = await api("/home/", { session: req.session });
  res.render("home", { title: "Украшения для пирсинга", ...data });
});

router.get("/contacts", async (req, res) => {
  const contacts = await api("/contacts/", { session: req.session });
  res.render("contacts", { title: "Контакты", contacts });
});

router.get("/about", async (req, res) => {
  const about = await api("/about/", { session: req.session });
  res.render("about", { title: "О магазине", about });
});

router.get("/delivery", async (req, res) => {
  const delivery = await api("/delivery/", { session: req.session });
  res.render("delivery", { title: "Доставка и оплата", delivery });
});

export default router;

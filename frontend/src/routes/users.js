/** Регистрация, вход и профиль покупателя. */
import { Router } from "express";

import { api, ApiError } from "../api.js";

const router = Router();

/** Сохраняет токен и переносит гостевую корзину в аккаунт. */
async function signIn(req, auth) {
  req.session.token = auth.token;
  req.session.user = auth.user;
  await api("/carts/merge/", {
    method: "POST",
    session: req.session,
    body: { session_key: req.session.cartSession },
  });
}

router.get("/login", (req, res) => {
  res.render("login", { title: "Вход", form: {}, error: null });
});

router.post("/login", async (req, res) => {
  try {
    const auth = await api("/users/login/", { method: "POST", body: req.body });
    await signIn(req, auth);
    req.session.flash = { type: "success", text: `Добро пожаловать, ${auth.user.username}` };
    res.redirect("/");
  } catch (error) {
    if (!(error instanceof ApiError) || error.status >= 500) throw error;
    res.status(400).render("login", { title: "Вход", form: req.body, error: error.message });
  }
});

router.get("/register", (req, res) => {
  res.render("register", { title: "Регистрация", form: {}, error: null });
});

router.post("/register", async (req, res) => {
  try {
    const auth = await api("/users/register/", { method: "POST", body: req.body });
    await signIn(req, auth);
    req.session.flash = { type: "success", text: "Аккаунт создан" };
    res.redirect("/");
  } catch (error) {
    if (!(error instanceof ApiError) || error.status >= 500) throw error;
    res.status(400).render("register", {
      title: "Регистрация",
      form: req.body,
      error: error.message,
    });
  }
});

router.post("/logout", async (req, res) => {
  await api("/users/logout/", { method: "POST", session: req.session }).catch(() => null);
  req.session.token = null;
  req.session.user = null;
  res.redirect("/");
});

router.get("/profile", async (req, res) => {
  if (!req.session.user) return res.redirect("/login");
  const profile = await api("/users/profile/", { session: req.session });
  res.render("profile", { title: "Профиль", profile, saved: req.query.saved === "1" });
});

router.post("/profile", async (req, res) => {
  if (!req.session.user) return res.redirect("/login");
  const profile = await api("/users/profile/", {
    method: "PATCH",
    session: req.session,
    body: {
      first_name: req.body.first_name,
      last_name: req.body.last_name,
      email: req.body.email,
      phone: req.body.phone,
    },
  });
  req.session.user = profile;
  res.redirect("/profile?saved=1");
});

export default router;

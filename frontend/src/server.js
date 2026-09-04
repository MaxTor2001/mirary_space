/** HTTP-сервер витрины Mirari на Express. */
import { randomUUID } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";

import express from "express";
import session from "express-session";
import morgan from "morgan";

import { api, ApiError } from "./api.js";
import cartsRouter from "./routes/carts.js";
import goodsRouter from "./routes/goods.js";
import mainRouter from "./routes/main.js";
import ordersRouter from "./routes/orders.js";
import seoRouter from "./routes/seo.js";
import usersRouter from "./routes/users.js";
import { SITE_URL } from "./site.js";

const dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3000;

app.set("view engine", "ejs");
app.set("views", path.join(dirname, "..", "views"));

/** За nginx: доверяем X-Forwarded-*, иначе secure-кука не выставится под HTTPS. */
const behindTls = process.env.SECURE_COOKIES === "1";
if (behindTls) app.set("trust proxy", 1);

app.use(morgan("tiny"));
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(dirname, "..", "public")));

/** robots.txt и sitemap.xml — до сессии: роботу не нужна ни кука, ни корзина. */
app.use("/", seoRouter);
app.use(
  session({
    secret: process.env.SESSION_SECRET || "mirari-dev-secret",
    resave: false,
    saveUninitialized: true,
    cookie: { httpOnly: true, secure: behindTls, maxAge: 1000 * 60 * 60 * 24 * 14 },
  }),
);

/** Каждому гостю выдаётся ключ, по которому бэкенд хранит его корзину. */
app.use((req, res, next) => {
  if (!req.session.cartSession) req.session.cartSession = randomUUID();
  next();
});

/** Общие для всех шаблонов данные: пользователь, счётчик корзины, флеш-сообщение. */
app.use(async (req, res, next) => {
  res.locals.user = req.session.user || null;
  res.locals.shopName = "Mirari";
  res.locals.siteUrl = SITE_URL;
  res.locals.canonicalPath = null;
  res.locals.adminUrl = process.env.ADMIN_URL || "";
  res.locals.metrikaId = process.env.YANDEX_METRIKA_ID || "";
  res.locals.yandexVerification = process.env.YANDEX_VERIFICATION || "";
  res.locals.googleVerification = process.env.GOOGLE_SITE_VERIFICATION || "";
  res.locals.flash = req.session.flash || null;
  res.locals.currentPath = req.path;
  res.locals.price = (value) =>
    `${Number(value).toLocaleString("ru-RU", { maximumFractionDigits: 2 })} \u20bd`;
  // Размеры приходят списком строк («1.2», «10.0») — показываем через косую черту.
  res.locals.sizes = (values) =>
    (values || []).map(Number).join(" / ");
  // Выбранные покупателем размеры позиции: «1.2 × 8 мм».
  res.locals.chosen = (item) =>
    [item.thickness, item.length].filter(Boolean).map(Number).join(" \u00d7 ");
  req.session.flash = null;

  try {
    const cart = await api("/carts/", { session: req.session });
    res.locals.cartCount = cart.total_quantity;
  } catch {
    res.locals.cartCount = 0;
  }
  next();
});

app.use("/", mainRouter);
app.use("/", goodsRouter);
app.use("/cart", cartsRouter);
app.use("/orders", ordersRouter);
app.use("/", usersRouter);

app.use((req, res) => {
  res.status(404).render("error", {
    title: "Страница не найдена",
    message: "Такой страницы нет",
    noindex: true,
  });
});

app.use((err, req, res, _next) => {
  console.error(err);
  const status = err instanceof ApiError ? err.status : 500;
  res.status(status).render("error", { title: "Ошибка", message: err.message, noindex: true });
});

app.listen(PORT, () => console.log(`Mirari frontend слушает порт ${PORT}`));

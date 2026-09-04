/** robots.txt и карта сайта для поисковых роботов. */
import { Router } from "express";

import { api } from "../api.js";
import { SITE_URL } from "../site.js";

const router = Router();

/** Личные разделы: роботу там нечего индексировать, он получит редирект на вход. */
const PRIVATE_PREFIXES = ["/cart", "/orders", "/profile", "/login", "/register", "/logout"];

/* Подтверждение владения доменом для IndexNow: поисковик забирает ключ по этому
   адресу и сверяет с тем, что пришло в уведомлении. Отдаём из .env, без файла. */
const INDEXNOW_KEY = process.env.INDEXNOW_KEY || "";
if (INDEXNOW_KEY) {
  router.get(`/${INDEXNOW_KEY}.txt`, (req, res) => res.type("text/plain").send(INDEXNOW_KEY));
}

router.get("/robots.txt", (req, res) => {
  const lines = [
    "User-agent: *",
    ...PRIVATE_PREFIXES.map((p) => `Disallow: ${p}`),
    "",
    `Sitemap: ${SITE_URL}/sitemap.xml`,
    "",
  ];
  res.type("text/plain").send(lines.join("\n"));
});

/** Карта сайта: статические страницы плюс все категории и товары из каталога. */
router.get("/sitemap.xml", async (req, res) => {
  const [categories, products] = await Promise.all([
    api("/goods/categories/"),
    api("/goods/products/?page_size=1000"),
  ]);

  const urls = [
    { loc: "/", priority: "1.0", changefreq: "daily" },
    { loc: "/catalog", priority: "0.9", changefreq: "daily" },
    { loc: "/about", priority: "0.4", changefreq: "yearly" },
    { loc: "/delivery", priority: "0.5", changefreq: "yearly" },
    { loc: "/contacts", priority: "0.4", changefreq: "yearly" },
    ...categories.map((c) => ({
      loc: `/catalog?category=${encodeURIComponent(c.slug)}`,
      priority: "0.7",
      changefreq: "weekly",
    })),
    ...(products.results || products).map((p) => ({
      loc: `/product/${p.slug}`,
      priority: "0.8",
      changefreq: "weekly",
    })),
  ];

  const body = urls
    .map(
      ({ loc, priority, changefreq }) =>
        `  <url><loc>${SITE_URL}${loc.replace(/&/g, "&amp;")}</loc>` +
        `<changefreq>${changefreq}</changefreq><priority>${priority}</priority></url>`,
    )
    .join("\n");

  res.type("application/xml").send(
    `<?xml version="1.0" encoding="UTF-8"?>\n` +
      `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>\n`,
  );
});

export default router;

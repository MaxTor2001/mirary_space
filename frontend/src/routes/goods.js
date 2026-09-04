/** Каталог и карточка товара. */
import { Router } from "express";

import { api } from "../api.js";

const router = Router();

router.get("/catalog", async (req, res) => {
  const { category = "", search = "", ordering = "", page = "1" } = req.query;
  const params = new URLSearchParams({ page });
  if (category) params.set("category__slug", category);
  if (search) params.set("search", search);
  if (ordering) params.set("ordering", ordering);

  const [products, categories] = await Promise.all([
    api(`/goods/products/?${params}`, { session: req.session }),
    api("/goods/categories/", { session: req.session }),
  ]);

  const active = categories.find((c) => c.slug === category);
  res.render("catalog", {
    title: active ? active.name : "Каталог",
    products,
    categories,
    filters: { category, search, ordering },
    page: Number(page),
    // Страницы фильтров и пагинации сводятся к адресу категории: у них один текст.
    canonicalPath: active ? `/catalog?category=${active.slug}` : "/catalog",
    description: active
      ? `${active.name}: ${active.description} Купить в интернет-магазине Mirari с доставкой по России.`
      : undefined,
  });
});

router.get("/product/:slug", async (req, res) => {
  const product = await api(`/goods/products/${req.params.slug}/`, { session: req.session });
  // В каталоге прочерк означает «не указано» — в описание для выдачи он не годится.
  const material = product.material === "—" ? "" : product.material;
  const size = [product.thicknesses, product.lengths]
    .map((values) => values.map(Number).join("/"))
    .filter(Boolean)
    .join("x");
  res.render("product", {
    title: product.name,
    product,
    canonicalPath: `/product/${product.slug}`,
    description: [product.name, material, size && `${size} мм`].filter(Boolean).join(", ") +
      ". Купить в интернет-магазине Mirari с доставкой по России.",
  });
});

export default router;

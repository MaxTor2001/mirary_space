# Mirari — интернет-магазин товаров для пирсинга

Монолит на Django (API) + витрина на Node.js (Express + EJS) + PostgreSQL. Всё поднимается одной командой в Docker.

## Запуск

```bash
cp .env.example .env      # по желанию: поменять пароли и порты
docker compose up -d --build
```

- Витрина: http://localhost:3000
- API: http://localhost:8000/api/
- Админка: http://localhost:8000/admin/ (`admin` / `admin`)

При первом старте бэкенд применяет миграции, собирает статику и загружает демо-каталог
(`SEED_DEMO=0` в `.env` отключает наполнение).

## Состав

| Сервис | Технологии | Порт |
|---|---|---|
| `db` | PostgreSQL 18 | 5432 |
| `backend` | Django 6 + DRF, gunicorn, uv | 8000 |
| `frontend` | Node.js 24, Express 5, EJS | 3000 |

## Приложения Django (`backend/`)

- **main** — контент главной страницы (баннеры, категории, новинки) и контакты.
- **goods** — каталог: категории и товары, фильтры, поиск, сортировка.
- **carts** — корзина пользователя или гостя (по ключу `X-Cart-Session`), слияние при входе.
- **orders** — оформление заказа из корзины, списание остатков, история заказов.
- **users** — кастомная модель пользователя, регистрация, вход по токену, профиль.

## API

```
GET  /api/home/                     баннеры, категории, новинки
GET  /api/contacts/                 контакты и реквизиты магазина
GET  /api/about/                    о магазине: история, преимущества, реквизиты
GET  /api/delivery/                 способы доставки, оплаты и условия возврата
GET  /api/goods/categories/         список категорий
GET  /api/goods/products/           ?search= &category__slug= &ordering= &page=
GET  /api/goods/products/<slug>/    карточка товара
GET  /api/carts/                    позиции корзины, сумма и количество
POST /api/carts/                    {product_id, quantity}
PATCH/DELETE /api/carts/<id>/       изменить количество / удалить
POST /api/carts/clear/              очистить корзину
POST /api/carts/merge/              {session_key} — перенести гостевую корзину
POST /api/users/register/           {username, email, password, ...} -> token
POST /api/users/login/              {username, password} -> token
POST /api/users/logout/
GET/PATCH /api/users/profile/
GET/POST /api/orders/               история и оформление заказа из корзины
GET  /api/orders/<id>/              детали заказа
```

Аутентификация — заголовок `Authorization: Token <token>`.
Корзина гостя — заголовок `X-Cart-Session: <uuid>` (фронтенд хранит его в своей сессии).

## Страницы витрины (`frontend/`)

`/` главная · `/catalog` каталог с фильтрами · `/product/:slug` карточка ·
`/cart` корзина · `/orders/checkout` оформление · `/orders` заказы ·
`/login`, `/register`, `/profile`, `/contacts`, `/about`, `/delivery`.

## Деплой на сервер

Продакшен-оверлей `docker-compose.prod.yml`: БД без публикации портов, API только на
`127.0.0.1:8000`, наружу смотрит одна витрина на `SHOP_PUBLIC_PORT` (по умолчанию 8080).

```bash
rsync -az --exclude .venv --exclude node_modules --exclude .env ./ server:/path/mirari/
ssh server 'cd /path/mirari && docker compose -f docker-compose.yml -f docker-compose.prod.yml -p mirari up -d --build'
```

`.env` на сервере обязателен: `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS` со списком хостов
(включая `backend` — под этим именем витрина ходит в API) и `DJANGO_ADMIN_PASSWORD`, иначе
`seed_demo` создаст администратора с паролем `admin`.

За nginx: `SHOP_BIND=127.0.0.1` убирает порт витрины с внешнего интерфейса, `SECURE_COOKIES=1`
включает `trust proxy` и флаг `Secure` у куки сессии. Пример vhost — `deploy/nginx/mirari.conf.example`.

## Поисковая выдача

`robots.txt` и `sitemap.xml` отдаёт витрина (`frontend/src/routes/seo.js`), карта собирается
из каталога на лету. Счётчик Метрики, подтверждения владения и IndexNow включаются
переменными в `.env` — порядок действий в [docs/SEO.md](docs/SEO.md).

## Разработка без Docker

```bash
# бэкенд (нужен запущенный postgres)
cd backend && uv sync && uv run manage.py migrate && uv run manage.py runserver

# фронтенд
cd frontend && npm install && API_URL=http://localhost:8000/api npm run dev
```

## Полезные команды

```bash
docker compose logs -f backend        # логи
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo
docker compose down -v                # снести стек вместе с данными
```

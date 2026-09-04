# Mirari — заметки для работы в репозитории

Монолит Django (API, порт 8000) + витрина Node.js/Express+EJS (порт 3000) + PostgreSQL. Описание
структуры и API — в `README.md`, здесь только рабочие правила и подводные камни.

## Рабочий цикл

- Всё запускается через `docker compose up -d --build`; после правок бэкенда достаточно
  `docker compose restart backend`, миграции и `seed_demo` выполняет `backend/entrypoint.sh`.
- Python-команды локально — только через `uv run` из `backend/` (`uv run manage.py ...`), зависимости — `uv add`.
- Новые модели: `uv run manage.py makemigrations` локально (подключение к БД не требуется), миграции коммитим.

## Подводные камни

- `postgres:18` хранит данные в `/var/lib/postgresql`, а не в `/var/lib/postgresql/data`. Том смонтирован
  на `/var/lib/postgresql`; менять обратно нельзя — контейнер БД падает на старте.
- Витрина не имеет своей БД: любые новые данные на странице сначала появляются как эндпоинт DRF,
  затем как вызов `api()` в `frontend/src/routes/*.js`.
- Корзина гостя опознаётся заголовком `X-Cart-Session`; при добавлении нового эндпоинта корзины
  используйте `carts/services.py: cart_owner()`, а не обращение к `request.user` напрямую.

## Стиль

- Комментарии — короткие docstring на русском, по одному на модуль/нетривиальный метод; без защитного кода.
- Приложения Django плоские: `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`.

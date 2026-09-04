#!/bin/sh
# Выкатка Mirari на сервере: забрать код из git и пересобрать контейнеры.
#
#   ssh fstek '/home/deploy/mirari/deploy/deploy.sh'
#
# .env не трогается: он в .gitignore, reset --hard его не видит.
set -e

cd "$(dirname "$0")/.."

# Какие compose-файлы читать, задаёт COMPOSE_FILE в .env. Без него docker compose
# возьмёт только базовый файл и поднимет dev-конфигурацию: Postgres наружу,
# витрина не на том порту. Лучше остановиться здесь, чем выкатить это на прод.
grep -q '^COMPOSE_FILE=' .env || { echo "В .env нет COMPOSE_FILE — выкатка остановлена"; exit 1; }

echo "== было =="
git log --oneline -1

git fetch origin main
git reset --hard origin/main

echo "== стало =="
git log --oneline -1

docker compose up -d --build

echo "== проверка =="
sleep 8
curl -sf -o /dev/null -w "витрина: %{http_code}\n" http://127.0.0.1:8080/
ADMIN_PATH=$(grep '^DJANGO_ADMIN_PATH=' .env | cut -d= -f2)
curl -s -o /dev/null -w "админка: %{http_code}\n" "http://127.0.0.1:8000/${ADMIN_PATH:-admin/}"

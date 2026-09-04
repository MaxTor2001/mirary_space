#!/bin/sh
# Выкатка Mirari на сервере: забрать код из git и пересобрать контейнеры.
#
#   ssh fstek '/home/deploy/mirari/deploy/deploy.sh'
#
# .env не трогается: он в .gitignore, reset --hard его не видит.
set -e

cd "$(dirname "$0")/.."

echo "== было =="
git log --oneline -1

git fetch origin main
git reset --hard origin/main

echo "== стало =="
git log --oneline -1

docker compose -f docker-compose.yml -f docker-compose.prod.yml -p mirari up -d --build

echo "== проверка =="
sleep 8
curl -sf -o /dev/null -w "витрина: %{http_code}\n" http://127.0.0.1:8080/
curl -s -o /dev/null -w "админка: %{http_code}\n" http://127.0.0.1:8000/admin/

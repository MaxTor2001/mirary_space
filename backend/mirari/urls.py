"""Корневая маршрутизация проекта Mirari."""
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Адрес админки задаётся в .env: на проде он не /admin/, чтобы форма входа
# не висела по угадываемому адресу. Значение должно совпадать с location в nginx.
ADMIN_PATH = os.environ.get("DJANGO_ADMIN_PATH", "admin/")

urlpatterns = [
    path(ADMIN_PATH, admin.site.urls),
    path("api/", include("main.urls")),
    path("api/users/", include("users.urls")),
    path("api/goods/", include("goods.urls")),
    path("api/carts/", include("carts.urls")),
    path("api/orders/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

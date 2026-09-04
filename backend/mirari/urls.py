"""Корневая маршрутизация проекта Mirari."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("main.urls")),
    path("api/users/", include("users.urls")),
    path("api/goods/", include("goods.urls")),
    path("api/carts/", include("carts.urls")),
    path("api/orders/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

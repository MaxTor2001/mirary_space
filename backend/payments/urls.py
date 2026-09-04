from django.urls import path

from .views import availability, create, sync, webhook

urlpatterns = [
    path("", create, name="payment-create"),
    path("enabled/", availability, name="payment-enabled"),
    path("sync/", sync, name="payment-sync"),
    path("webhook/", webhook, name="payment-webhook"),
]

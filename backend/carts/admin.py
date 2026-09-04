from django.contrib import admin

from .models import Cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("__str__", "quantity", "created_at")
    list_filter = ("created_at",)

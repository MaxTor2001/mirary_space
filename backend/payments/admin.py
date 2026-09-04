from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount", "status", "external_id", "created_at")
    list_filter = ("status",)
    search_fields = ("external_id", "order__id")
    readonly_fields = ("external_id", "amount", "confirmation_url", "created_at", "updated_at")

from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "phone", "status", "is_paid", "created_at")
    list_filter = ("status", "is_paid", "requires_delivery")
    inlines = (OrderItemInline,)

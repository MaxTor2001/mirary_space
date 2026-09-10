from django.contrib import admin

from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "sort")
    list_editable = ("is_active", "sort")


admin.site.site_header = "Mirari"
admin.site.site_title = "Mirari"
admin.site.index_title = "Управление магазином"

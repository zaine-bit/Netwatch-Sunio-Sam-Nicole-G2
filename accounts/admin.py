from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_active", "created_at")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("role", "is_active")
    exclude = ("password",)
    readonly_fields = ("created_at", "updated_at")

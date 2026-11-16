from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "contact_number", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "contact_number")
    readonly_fields = ("created_at", "updated_at")

from django.db import models


class Account(models.Model):
    """Application account; independent of Django's built-in User model."""

    ROLE_ADMIN = "admin"
    ROLE_OWNER = "owner"
    ROLE_CHOICES = [(ROLE_ADMIN, "Administrator"), (ROLE_OWNER, "Network Owner")]

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_OWNER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_account"
        ordering = ["username"]

    def __str__(self):
        return self.username

from django.db import models
from django.db.models import Q


class Account(models.Model):
    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = ((ROLE_OWNER, "Network Owner"), (ROLE_ADMIN, "Administrator"))

    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_OWNER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_account"
        ordering = ["username"]

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Device(models.Model):
    STATUS_ACTIVE = "Active"
    STATUS_REMOVED = "Removed"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_REMOVED, "Removed"),
    )

    user = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50)
    mac_address = models.CharField(max_length=17, unique=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    class Meta:
        ordering = ["device_name", "id"]

    def __str__(self):
        return f"{self.device_name} ({self.mac_address})"


class UsageLog(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="usage_logs",
    )
    usage_date = models.DateField()
    data_used_mb = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-usage_date", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(data_used_mb__gte=0),
                name="usage_data_used_mb_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.device.device_name}: {self.data_used_mb} MB on {self.usage_date}"


class Alert(models.Model):
    STATUS_UNREAD = "Unread"
    STATUS_ACKNOWLEDGED = "Acknowledged"
    STATUS_CHOICES = (
        (STATUS_UNREAD, "Unread"),
        (STATUS_ACKNOWLEDGED, "Acknowledged"),
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    usage_log = models.ForeignKey(
        UsageLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
    )
    alert_date = models.DateTimeField(auto_now_add=True)
    usage_amount = models.DecimalField(max_digits=10, decimal_places=2)
    baseline_average = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_UNREAD,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-alert_date", "-id"]

    def __str__(self):
        return f"{self.device.device_name}: unusual usage on {self.alert_date:%Y-%m-%d}"

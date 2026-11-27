import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_custom_account"),
    ]

    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("device_name", models.CharField(max_length=100)),
                ("device_type", models.CharField(max_length=50)),
                ("mac_address", models.CharField(max_length=17, unique=True)),
                ("date_registered", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("Active", "Active"), ("Removed", "Removed")], default="Active", max_length=20)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="devices", to="accounts.account")),
            ],
            options={
                "ordering": ["device_name", "id"],
            },
        ),
    ]

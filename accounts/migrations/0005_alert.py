# Generated for the NetWatch alert feature.
import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("accounts", "0004_usage_log")]
    operations = [
        migrations.CreateModel(
            name="Alert",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("alert_date", models.DateTimeField(auto_now_add=True)),
                ("usage_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("baseline_average", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("Unread", "Unread"), ("Acknowledged", "Acknowledged")], default="Unread", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="accounts.device")),
                ("usage_log", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="alerts", to="accounts.usagelog")),
            ],
            options={"ordering": ["-alert_date", "-id"]},
        ),
    ]

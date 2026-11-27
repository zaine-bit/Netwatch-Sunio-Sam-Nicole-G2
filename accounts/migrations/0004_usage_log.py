from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_device"),
    ]

    operations = [
        migrations.CreateModel(
            name="UsageLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("usage_date", models.DateField()),
                ("data_used_mb", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("device", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="usage_logs", to="accounts.device")),
            ],
            options={
                "ordering": ["-usage_date", "-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="usagelog",
            constraint=models.CheckConstraint(
                condition=models.Q(("data_used_mb__gte", 0)),
                name="usage_data_used_mb_non_negative",
            ),
        ),
    ]

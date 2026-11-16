from django.conf import settings
from django.db import migrations, models


def copy_existing_users(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    Account = apps.get_model("accounts", "Account")
    seen_usernames, seen_emails = set(), set()
    for user in User.objects.all().iterator():
        username = (user.username or f"user{user.pk}").strip()[:30]
        if username.lower() in seen_usernames:
            suffix = str(user.pk)
            username = f"{username[:30-len(suffix)-1]}_{suffix}"
        seen_usernames.add(username.lower())
        email = (user.email or "").strip().lower()[:254]
        if not email or email in seen_emails:
            email = f"legacy-{user.pk}@invalid.local"
        seen_emails.add(email)
        Account.objects.create(
            username=username, email=email, password=user.password,
            first_name=user.first_name or "", last_name=user.last_name or "",
            role="admin" if user.is_staff else "owner", is_active=user.is_active,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=30, unique=True)),
                ("email", models.CharField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("contact_number", models.CharField(blank=True, max_length=20)),
                ("role", models.CharField(choices=[("owner", "Network Owner"), ("admin", "Administrator")], default="owner", max_length=10)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "accounts_account", "ordering": ["username"]},
        ),
        migrations.RunPython(copy_existing_users, migrations.RunPython.noop),
        migrations.DeleteModel(name="Profile"),
    ]

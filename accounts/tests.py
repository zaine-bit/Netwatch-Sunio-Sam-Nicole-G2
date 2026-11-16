from django.test import TestCase
from django.urls import reverse
from .models import Account


class AccountFeatureTests(TestCase):
    def test_registration_creates_custom_account(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "networkowner", "email": "owner@example.com",
            "first_name": "Network", "last_name": "Owner",
            "password": "StrongPassword!234", "confirm_password": "StrongPassword!234",
        })
        self.assertRedirects(response, reverse("accounts:login"))
        account = Account.objects.get(username="networkowner")
        self.assertNotEqual(account.password, "StrongPassword!234")

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        from django.contrib.auth.hashers import make_password
        Account.objects.create(username="existing", email="owner@example.com", password=make_password("StrongPassword!234"))
        response = self.client.post(reverse("accounts:register"), {
            "username": "another", "email": "OWNER@example.com",
            "password": "StrongPassword!234", "confirm_password": "StrongPassword!234",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_dashboard_requires_custom_session(self):
        response = self.client.get(reverse("accounts:user_dashboard"))
        self.assertRedirects(response, reverse("accounts:login"))

    def test_login_accepts_username_and_password(self):
        from django.contrib.auth.hashers import make_password
        Account.objects.create(username="member", email="member@example.com", password=make_password("StrongPassword!234"))
        response = self.client.post(reverse("accounts:login"), {"identifier": "member", "password": "StrongPassword!234"})
        self.assertRedirects(response, reverse("accounts:dashboard_redirect"))
        self.assertIn("account_id", self.client.session)

    def test_regular_account_cannot_open_admin_dashboard(self):
        account = Account.objects.create(username="member", email="member@example.com", password="unused")
        session = self.client.session
        session["account_id"] = account.pk
        session.save()
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertRedirects(response, reverse("accounts:user_dashboard"))

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
        response = self.client.post(
            reverse("accounts:login"),
            {"identifier": "member", "password": "StrongPassword!234"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            (reverse("accounts:dashboard_redirect"), 302),
            response.redirect_chain,
        )
        self.assertIn("account_id", self.client.session)

    def test_regular_account_cannot_open_admin_dashboard(self):
        account = Account.objects.create(username="member", email="member@example.com", password="unused")
        session = self.client.session
        session["account_id"] = account.pk
        session.save()
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertRedirects(response, reverse("accounts:user_dashboard"))

    def test_logout_clears_custom_account_session(self):
        account = Account.objects.create(
            username="logoutmember", email="logout@example.com", password="unused"
        )
        session = self.client.session
        session["account_id"] = account.pk
        session.save()

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("account_id", self.client.session)

    def test_inactive_account_session_is_cleared(self):
        account = Account.objects.create(
            username="inactive", email="inactive@example.com",
            password="unused", is_active=False,
        )
        session = self.client.session
        session["account_id"] = account.pk
        session.save()

        response = self.client.get(reverse("accounts:user_dashboard"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("account_id", self.client.session)

    def test_profile_update_changes_only_signed_in_account(self):
        account = Account.objects.create(
            username="profileowner", email="profile@example.com", password="unused"
        )
        other = Account.objects.create(
            username="otherowner", email="other@example.com", password="unused"
        )
        session = self.client.session
        session["account_id"] = account.pk
        session.save()

        response = self.client.post(reverse("accounts:profile"), {
            "username": "profileowner",
            "email": "updated@example.com",
            "first_name": "Updated",
            "last_name": "Owner",
            "contact_number": "09171234567",
        })

        self.assertRedirects(response, reverse("accounts:profile"))
        account.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(account.email, "updated@example.com")
        self.assertEqual(account.first_name, "Updated")
        self.assertEqual(other.email, "other@example.com")

    def test_administrator_cannot_open_owner_dashboard(self):
        admin = Account.objects.create(
            username="siteadmin", email="admin@example.com",
            password="unused", role=Account.ROLE_ADMIN,
        )
        session = self.client.session
        session["account_id"] = admin.pk
        session.save()

        response = self.client.get(reverse("accounts:user_dashboard"))

        self.assertRedirects(response, reverse("accounts:admin_dashboard"))


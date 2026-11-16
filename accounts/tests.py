from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountFeatureTests(TestCase):
    def test_registration_creates_regular_user_and_profile(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "networkowner",
            "email": "owner@example.com",
            "first_name": "Network",
            "last_name": "Owner",
            "password1": "StrongPassword!234",
            "password2": "StrongPassword!234",
        })
        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(username="networkowner")
        self.assertTrue(user.check_password("StrongPassword!234"))
        self.assertFalse(user.is_staff)
        self.assertTrue(hasattr(user, "profile"))

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(username="existing", email="owner@example.com", password="StrongPassword!234")
        response = self.client.post(reverse("accounts:register"), {
            "username": "another",
            "email": "OWNER@example.com",
            "first_name": "Another",
            "last_name": "Owner",
            "password1": "StrongPassword!234",
            "password2": "StrongPassword!234",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("accounts:user_dashboard"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:user_dashboard')}")

    def test_regular_user_cannot_open_admin_dashboard(self):
        user = User.objects.create_user(username="member", password="StrongPassword!234")
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertRedirects(response, reverse("accounts:user_dashboard"))

    def test_staff_user_cannot_open_regular_dashboard(self):
        admin = User.objects.create_user(username="operator", password="StrongPassword!234", is_staff=True)
        self.client.force_login(admin)
        response = self.client.get(reverse("accounts:user_dashboard"))
        self.assertRedirects(response, reverse("accounts:admin_dashboard"))

    def test_profile_page_requires_login_and_shows_own_account(self):
        user = User.objects.create_user(username="privateuser", email="private@example.com", password="StrongPassword!234")
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "private@example.com")

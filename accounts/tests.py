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

    def test_registration_rejects_duplicate_username_case_insensitively(self):
        from django.contrib.auth.hashers import make_password
        Account.objects.create(
            username="TakenName", email="taken@example.com",
            password=make_password("StrongPassword!234"),
        )
        response = self.client.post(reverse("accounts:register"), {
            "username": "takenname",
            "email": "new@example.com",
            "password": "StrongPassword!234",
            "confirm_password": "StrongPassword!234",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "username is already taken")

    def test_profile_rejects_another_accounts_email(self):
        account = Account.objects.create(
            username="profileone", email="one@example.com", password="unused"
        )
        Account.objects.create(
            username="profiletwo", email="two@example.com", password="unused"
        )
        session = self.client.session
        session["account_id"] = account.pk
        session.save()

        response = self.client.post(reverse("accounts:profile"), {
            "username": "profileone",
            "email": "TWO@example.com",
            "first_name": "",
            "last_name": "",
            "contact_number": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already in use")
        account.refresh_from_db()
        self.assertEqual(account.email, "one@example.com")



from .models import Device


class DeviceManagementTests(TestCase):
    def setUp(self):
        self.owner = Account.objects.create(
            username="ownerone", email="ownerone@example.com", password="unused"
        )
        self.other_owner = Account.objects.create(
            username="ownertwo", email="ownertwo@example.com", password="unused"
        )
        session = self.client.session
        session["account_id"] = self.owner.pk
        session.save()

    def test_owner_can_register_device(self):
        response = self.client.post(reverse("accounts:device_create"), {
            "device_name": "Living Room Laptop",
            "device_type": "Laptop",
            "mac_address": "aa:bb:cc:dd:ee:01",
        })
        self.assertRedirects(response, reverse("accounts:device_list"))
        device = Device.objects.get(mac_address="AA:BB:CC:DD:EE:01")
        self.assertEqual(device.user, self.owner)
        self.assertEqual(device.status, Device.STATUS_ACTIVE)

    def test_device_list_only_shows_signed_in_owners_devices(self):
        own = Device.objects.create(
            user=self.owner, device_name="My Phone", device_type="Phone",
            mac_address="AA:BB:CC:DD:EE:02",
        )
        Device.objects.create(
            user=self.other_owner, device_name="Other Laptop", device_type="Laptop",
            mac_address="AA:BB:CC:DD:EE:03",
        )
        response = self.client.get(reverse("accounts:device_list"))
        self.assertContains(response, own.device_name)
        self.assertNotContains(response, "Other Laptop")

    def test_owner_cannot_edit_another_owners_device(self):
        other_device = Device.objects.create(
            user=self.other_owner, device_name="Private Laptop", device_type="Laptop",
            mac_address="AA:BB:CC:DD:EE:04",
        )
        response = self.client.get(
            reverse("accounts:device_update", args=[other_device.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_owner_cannot_remove_another_owners_device(self):
        other_device = Device.objects.create(
            user=self.other_owner, device_name="Private Phone", device_type="Phone",
            mac_address="AA:BB:CC:DD:EE:05",
        )
        response = self.client.post(
            reverse("accounts:device_delete", args=[other_device.pk])
        )
        self.assertEqual(response.status_code, 404)
        other_device.refresh_from_db()
        self.assertEqual(other_device.status, Device.STATUS_ACTIVE)

    def test_remove_marks_device_removed_instead_of_deleting_it(self):
        device = Device.objects.create(
            user=self.owner, device_name="Old Tablet", device_type="Tablet",
            mac_address="AA:BB:CC:DD:EE:06",
        )
        response = self.client.post(
            reverse("accounts:device_delete", args=[device.pk])
        )
        self.assertRedirects(response, reverse("accounts:device_list"))
        device.refresh_from_db()
        self.assertEqual(device.status, Device.STATUS_REMOVED)

    def test_invalid_mac_address_is_rejected(self):
        response = self.client.post(reverse("accounts:device_create"), {
            "device_name": "Invalid Device",
            "device_type": "Laptop",
            "mac_address": "not-a-mac",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid MAC address")
        self.assertFalse(Device.objects.filter(device_name="Invalid Device").exists())

    def test_duplicate_mac_address_is_rejected(self):
        Device.objects.create(
            user=self.other_owner, device_name="Existing Device", device_type="Laptop",
            mac_address="AA:BB:CC:DD:EE:07",
        )
        response = self.client.post(reverse("accounts:device_create"), {
            "device_name": "Duplicate Device",
            "device_type": "Phone",
            "mac_address": "aa:bb:cc:dd:ee:07",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Device.objects.filter(device_name="Duplicate Device").exists())



from datetime import timedelta
from django.utils import timezone
from .models import UsageLog


class UsageTrackingTests(TestCase):
    def setUp(self):
        self.owner = Account.objects.create(
            username="usageowner", email="usageowner@example.com", password="unused"
        )
        self.other_owner = Account.objects.create(
            username="otherusage", email="otherusage@example.com", password="unused"
        )
        self.device = Device.objects.create(
            user=self.owner, device_name="Owner Laptop", device_type="Laptop",
            mac_address="AA:BB:CC:DD:EE:21",
        )
        self.other_device = Device.objects.create(
            user=self.other_owner, device_name="Other Owner Phone", device_type="Phone",
            mac_address="AA:BB:CC:DD:EE:22",
        )
        session = self.client.session
        session["account_id"] = self.owner.pk
        session.save()

    def test_owner_can_record_daily_usage_for_own_device(self):
        response = self.client.post(
            reverse("accounts:usage_create", args=[self.device.pk]),
            {"usage_date": timezone.localdate().isoformat(), "data_used_mb": "125.50"},
        )
        self.assertRedirects(
            response, reverse("accounts:usage_list", args=[self.device.pk])
        )
        usage = UsageLog.objects.get(device=self.device)
        self.assertEqual(str(usage.data_used_mb), "125.50")
        self.assertEqual(usage.device, self.device)

    def test_usage_history_only_shows_records_for_selected_owned_device(self):
        UsageLog.objects.create(
            device=self.device, usage_date=timezone.localdate(), data_used_mb="80.00"
        )
        response = self.client.get(
            reverse("accounts:usage_list", args=[self.other_device.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_owner_cannot_record_usage_for_another_owners_device(self):
        response = self.client.post(
            reverse("accounts:usage_create", args=[self.other_device.pk]),
            {"usage_date": timezone.localdate().isoformat(), "data_used_mb": "25"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(UsageLog.objects.count(), 0)

    def test_negative_usage_is_rejected(self):
        response = self.client.post(
            reverse("accounts:usage_create", args=[self.device.pk]),
            {"usage_date": timezone.localdate().isoformat(), "data_used_mb": "-1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be negative")
        self.assertEqual(UsageLog.objects.count(), 0)

    def test_future_usage_date_is_rejected(self):
        future_date = (timezone.localdate() + timedelta(days=1)).isoformat()
        response = self.client.post(
            reverse("accounts:usage_create", args=[self.device.pk]),
            {"usage_date": future_date, "data_used_mb": "20"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be in the future")
        self.assertEqual(UsageLog.objects.count(), 0)

    def test_removed_device_cannot_receive_new_usage_records(self):
        self.device.status = Device.STATUS_REMOVED
        self.device.save(update_fields=["status"])
        response = self.client.get(
            reverse("accounts:usage_create", args=[self.device.pk])
        )
        self.assertEqual(response.status_code, 404)

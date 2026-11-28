import re
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import account_login_required
from .models import Account, Alert, Device, UsageLog

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,30}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")


def _render(request, template, context=None, status=200):
    data = {"account": getattr(request, "account", None)}
    if context:
        data.update(context)
    return render(request, template, data, status=status)


def register(request):
    if request.session.get("account_id"):
        return redirect("accounts:dashboard_redirect")
    errors = {}
    values = {key: "" for key in ("username", "email", "first_name", "last_name")}
    if request.method == "POST":
        values.update({key: request.POST.get(key, "").strip() for key in values})
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")
        username = values["username"]
        email = values["email"].lower()
        if not USERNAME_RE.fullmatch(username):
            errors["username"] = "Use 3–30 characters: letters, numbers, dots, underscores, or hyphens."
        elif Account.objects.filter(username__iexact=username).exists():
            errors["username"] = "That username is already taken."
        if len(email) > 254 or not EMAIL_RE.fullmatch(email):
            errors["email"] = "Enter a valid email address."
        elif Account.objects.filter(email__iexact=email).exists():
            errors["email"] = "An account with this email already exists."
        if password != confirm:
            errors["confirm_password"] = "The passwords do not match."
        try:
            validate_password(password)
        except ValidationError as exc:
            errors["password"] = " ".join(exc.messages)
        if not errors:
            with transaction.atomic():
                Account.objects.create(
                    username=username, email=email, first_name=values["first_name"],
                    last_name=values["last_name"], password=make_password(password),
                )
            messages.success(request, "Your account was created. You can now log in.")
            return redirect("accounts:login")
    return _render(request, "accounts/register.html", {"errors": errors, "values": values})


def login(request):
    if request.session.get("account_id"):
        return redirect("accounts:dashboard_redirect")
    error = ""
    identifier = ""
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")
        account = Account.objects.filter(is_active=True).filter(
            models_q_username_or_email(identifier)
        ).first()
        if account and check_password(password, account.password):
            request.session.cycle_key()
            request.session["account_id"] = account.pk
            return redirect("accounts:dashboard_redirect")
        error = "Invalid username/email or password."
    return _render(request, "accounts/login.html", {"error": error, "identifier": identifier})


def models_q_username_or_email(identifier):
    from django.db.models import Q
    return Q(username__iexact=identifier) | Q(email__iexact=identifier)


@account_login_required
def dashboard_redirect(request):
    if request.account.role == Account.ROLE_ADMIN:
        return redirect("accounts:admin_dashboard")
    return redirect("accounts:user_dashboard")


@account_login_required
def admin_dashboard(request):
    if request.account.role != Account.ROLE_ADMIN:
        return redirect("accounts:user_dashboard")
    users = Account.objects.filter(role=Account.ROLE_OWNER).order_by("username")
    return _render(request, "accounts/admin_dashboard.html", {"users": users})


@account_login_required
def user_dashboard(request):
    if request.account.role == Account.ROLE_ADMIN:
        return redirect("accounts:admin_dashboard")
    devices = Device.objects.filter(user=request.account)
    alerts = Alert.objects.filter(device__user=request.account).select_related("device")[:5]
    unread_alert_count = Alert.objects.filter(
        device__user=request.account, status=Alert.STATUS_UNREAD
    ).count()
    recent_usage = UsageLog.objects.filter(
        device__user=request.account
    ).select_related("device")[:5]
    return _render(request, "accounts/user_dashboard.html", {
        "devices": devices,
        "alerts": alerts,
        "unread_alert_count": unread_alert_count,
        "recent_usage": recent_usage,
    })


@account_login_required
def profile(request):
    account = request.account
    errors = {}
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        contact_number = request.POST.get("contact_number", "").strip()
        if not USERNAME_RE.fullmatch(username):
            errors["username"] = "Use 3–30 valid username characters."
        elif Account.objects.filter(username__iexact=username).exclude(pk=account.pk).exists():
            errors["username"] = "That username is already taken."
        if len(email) > 254 or not EMAIL_RE.fullmatch(email):
            errors["email"] = "Enter a valid email address."
        elif Account.objects.filter(email__iexact=email).exclude(pk=account.pk).exists():
            errors["email"] = "That email address is already in use."
        if not errors:
            account.username, account.email = username, email
            account.first_name, account.last_name = first_name, last_name
            account.contact_number = contact_number
            account.save()
            messages.success(request, "Your profile was updated.")
            return redirect("accounts:profile")
        account.username, account.email = username, email
        account.first_name, account.last_name = first_name, last_name
        account.contact_number = contact_number
    return _render(request, "accounts/profile.html", {"errors": errors})


@require_POST
@account_login_required
def logout(request):
    request.session.flush()
    return redirect("accounts:login")


@account_login_required
def device_list(request):
    from .models import Device
    if request.account.role != Account.ROLE_OWNER:
        return redirect("accounts:admin_dashboard")
    devices = Device.objects.filter(user=request.account)
    return _render(request, "accounts/device_list.html", {"devices": devices})


@account_login_required
def device_create(request):
    from .forms import DeviceForm
    from .models import Device
    if request.account.role != Account.ROLE_OWNER:
        return redirect("accounts:admin_dashboard")
    form = DeviceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        device = form.save(commit=False)
        device.user = request.account
        device.save()
        messages.success(request, "Device registered successfully.")
        return redirect("accounts:device_list")
    return _render(request, "accounts/device_form.html", {"form": form, "page_title": "Register a device"})


@account_login_required
def device_update(request, device_id):
    from django.shortcuts import get_object_or_404
    from .forms import DeviceForm
    from .models import Device
    if request.account.role != Account.ROLE_OWNER:
        return redirect("accounts:admin_dashboard")
    device = get_object_or_404(Device, pk=device_id, user=request.account)
    form = DeviceForm(request.POST or None, instance=device)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Device details updated.")
        return redirect("accounts:device_list")
    return _render(request, "accounts/device_form.html", {"form": form, "page_title": "Edit device"})


@require_POST
@account_login_required
def device_delete(request, device_id):
    from django.shortcuts import get_object_or_404
    from .models import Device
    if request.account.role != Account.ROLE_OWNER:
        return redirect("accounts:admin_dashboard")
    device = get_object_or_404(Device, pk=device_id, user=request.account)
    device.status = Device.STATUS_REMOVED
    device.save(update_fields=["status"])
    messages.success(request, "Device marked as removed. Its history is retained.")
    return redirect("accounts:device_list")


@account_login_required
def usage_list(request, device_id):
    from django.shortcuts import get_object_or_404
    from .models import Device
    if request.account.role != Account.ROLE_OWNER:
        return redirect("accounts:admin_dashboard")
    device = get_object_or_404(Device, pk=device_id, user=request.account)
    usage_logs = device.usage_logs.all()
    return _render(request, "accounts/usage_list.html", {
        "device": device,
        "usage_logs": usage_logs,
    })


@account_login_required
def usage_create(request, device_id):
    from django.shortcuts import get_object_or_404
    from .forms import UsageLogForm
    if request.account.role != Account.ROLE_OWNER:
        return redirect("accounts:admin_dashboard")
    device = get_object_or_404(
        Device, pk=device_id, user=request.account, status=Device.STATUS_ACTIVE
    )
    form = UsageLogForm(
        request.POST or None,
        initial={"usage_date": timezone.localdate()},
    )
    if request.method == "POST" and form.is_valid():
        usage_log = form.save(commit=False)
        usage_log.device = device
        usage_log.save()

        # Compare this record with the same device's previous seven calendar days.
        baseline_start = usage_log.usage_date - timedelta(days=7)
        baseline = UsageLog.objects.filter(
            device=device,
            usage_date__gte=baseline_start,
            usage_date__lt=usage_log.usage_date,
        ).aggregate(average=Avg("data_used_mb"))["average"]

        if baseline is not None and usage_log.data_used_mb > baseline * 2:
            Alert.objects.get_or_create(
                usage_log=usage_log,
                defaults={
                    "device": device,
                    "usage_amount": usage_log.data_used_mb,
                    "baseline_average": baseline,
                },
            )
            messages.warning(
                request,
                "Unusual usage detected. An alert was added to your dashboard.",
            )
        else:
            messages.success(request, "Daily usage record saved.")
        return redirect("accounts:usage_list", device_id=device.pk)
    return _render(request, "accounts/usage_form.html", {
        "device": device,
        "form": form,
    })


@account_login_required
def alert_list(request):
    if request.account.role != Account.ROLE_OWNER:
        return redirect("accounts:admin_dashboard")
    alerts = Alert.objects.filter(
        device__user=request.account
    ).select_related("device")
    return _render(request, "accounts/alert_list.html", {"alerts": alerts})


@require_POST
@account_login_required
def alert_acknowledge(request, alert_id):
    from django.shortcuts import get_object_or_404
    if request.account.role != Account.ROLE_OWNER:
        return redirect("accounts:admin_dashboard")
    alert = get_object_or_404(
        Alert, pk=alert_id, device__user=request.account
    )
    alert.status = Alert.STATUS_ACKNOWLEDGED
    alert.save(update_fields=["status"])
    messages.success(request, "Alert acknowledged.")
    return redirect("accounts:alert_list")

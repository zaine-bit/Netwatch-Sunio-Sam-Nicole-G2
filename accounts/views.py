import re

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import account_login_required
from .models import Account

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
                account = Account.objects.create(
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
    return _render(request, "accounts/user_dashboard.html")


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

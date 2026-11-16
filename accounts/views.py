from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .decorators import account_login_required
from .models import Account
from .validators import validate_username, validate_account_email


@require_http_methods(["GET", "POST"])
def register_view(request):
    errors = []
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        try:
            username = validate_username(username)
        except ValidationError as exc:
            errors.extend(exc.messages)
        try:
            email = validate_account_email(email)
        except ValidationError as exc:
            errors.extend(exc.messages)
        if Account.objects.filter(username__iexact=username).exists():
            errors.append("That username is already taken.")
        if Account.objects.filter(email__iexact=email).exists():
            errors.append("That email address is already registered.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        try:
            validate_password(password)
        except ValidationError as exc:
            errors.extend(exc.messages)

        if not errors:
            try:
                account = Account.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),
                )
                request.session.cycle_key()
                request.session["account_id"] = account.pk
                return redirect("accounts:dashboard_redirect")
            except IntegrityError:
                errors.append("An account with those details already exists. Please try different details.")

    return render(request, "accounts/register.html", {"errors": errors})


@require_http_methods(["GET", "POST"])
def login_view(request):
    errors = []
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")
        account = Account.objects.filter(username__iexact=identifier).first()
        if account is None and "@" in identifier:
            account = Account.objects.filter(email__iexact=identifier).first()

        if account and account.is_active and check_password(password, account.password):
            request.session.cycle_key()
            request.session["account_id"] = account.pk
            return redirect("accounts:dashboard_redirect")
        errors.append("Invalid username/email or password.")

    return render(request, "accounts/login.html", {"errors": errors})


def logout_view(request):
    request.session.flush()
    return redirect("accounts:login")


@account_login_required
def dashboard_redirect(request):
    # Role-specific dashboards will be added in the dashboard phase.
    return render(request, "accounts/dashboard.html", {"account": request.account})

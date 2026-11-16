from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import ProfileForm, RegistrationForm
from .models import Profile

User = get_user_model()


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard_redirect")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, "Your account was created. You can now log in.")
            return redirect("accounts:login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard_redirect(request):
    if request.user.is_staff:
        return redirect("accounts:admin_dashboard")
    return redirect("accounts:user_dashboard")


@login_required
@user_passes_test(lambda user: user.is_staff, login_url=reverse_lazy("accounts:user_dashboard"))
def admin_dashboard(request):
    users = User.objects.filter(is_staff=False).order_by("username")
    return render(request, "accounts/admin_dashboard.html", {"users": users})


@login_required
@user_passes_test(lambda user: not user.is_staff, login_url=reverse_lazy("accounts:admin_dashboard"))
def user_dashboard(request):
    return render(request, "accounts/user_dashboard.html")


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile_obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=profile_obj, user=request.user)
    return render(request, "accounts/profile.html", {"form": form, "profile_user": request.user})

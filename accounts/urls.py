from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    AccountLoginView, admin_dashboard, dashboard_redirect, profile, register, user_dashboard,
)

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/user/", user_dashboard, name="user_dashboard"),
    path("profile/", profile, name="profile"),
]

from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/user/", views.user_dashboard, name="user_dashboard"),
    path("profile/", views.profile, name="profile"),
    path("devices/", views.device_list, name="device_list"),
    path("devices/add/", views.device_create, name="device_create"),
    path("devices/<int:device_id>/edit/", views.device_update, name="device_update"),
    path("devices/<int:device_id>/delete/", views.device_delete, name="device_delete"),
    path("devices/<int:device_id>/usage/", views.usage_list, name="usage_list"),
    path("devices/<int:device_id>/usage/add/", views.usage_create, name="usage_create"),
    path("alerts/", views.alert_list, name="alert_list"),
    path("alerts/<int:alert_id>/acknowledge/", views.alert_acknowledge, name="alert_acknowledge"),
]

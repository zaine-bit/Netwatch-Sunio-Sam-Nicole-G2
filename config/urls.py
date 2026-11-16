from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin is reserved for backend administration, not the main UI.
    path("django-admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("accounts.urls")),
]

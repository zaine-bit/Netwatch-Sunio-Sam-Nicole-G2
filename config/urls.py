from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/login/", permanent=False), name="home"),
    path("django-admin/", admin.site.urls),
    path("", include("accounts.urls")),
]

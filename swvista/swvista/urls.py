from django.contrib import admin
from django.urls import include, path

from .views import health, index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="healthz"),
    path("api/v1/auth/csrf/", index, name="index"),
    path("api/v1/auth/", include("rbac.urls")),
    path("api/v1/api/", include("api.urls")),
]

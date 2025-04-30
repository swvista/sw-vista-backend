from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("rbac.urls")),
    path("api/v1/api/", include("api.urls")),
]

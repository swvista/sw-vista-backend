from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.me_view, name="me"),
    path("user/", views.user, name="users"),
    path("role/", views.role, name="roles"),
    path("permission/", views.permission, name="permissions"),
    path("user_role/", views.user_role, name="user_role"),
    path("role_permission/", views.role_permission, name="role_permission"),
    path(
        "get_user_role_by_user_id/<int:user_id>/",
        views.get_user_role_by_user_id,
        name="get_user_role_by_user_id",
    ),
    path(
        "get_user_role_by_role_id/<int:role_id>/",
        views.get_user_role_by_role_id,
        name="get_user_role_by_role_id",
    ),
]

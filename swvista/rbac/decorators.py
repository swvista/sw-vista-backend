from functools import wraps

from django.http import JsonResponse
from django.utils import timezone

from .models import AuditLog, User


def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"error": "Authentication required."}, status=401)
        user_data = User.objects.get(id=user_id)
        if not user_data:
            return JsonResponse({"error": "Authentication required."}, status=401)
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def check_user_permission(permission_name):
    """
    Decorator factory to check if the logged-in user has a specific permission.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_permissions = request.session.get(
                "permissions", []
            )  # Default to empty list
            if not request.session.get("user_id"):  # Check login first
                return JsonResponse({"error": "Authentication required."}, status=401)

            # Ensure user_permissions is a set for contains check if it's stored as a list
            if isinstance(user_permissions, list):
                user_permissions = set(user_permissions)

            if permission_name in user_permissions:
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse(
                    {"error": "You do not have permission to access this resource."},
                    status=403,
                )

        return _wrapped_view

    return decorator


def audit_log(view_func):
    """
    Decorator to log the user's actions.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        AuditLog.objects.create(
            user=request.user,
            action=view_func.__name__,
            timestamp=timezone.now(),
            details=request.body,
        )

        return view_func(request, *args, **kwargs)

    return _wrapped_view

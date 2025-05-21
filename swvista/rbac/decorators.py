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


def check_user_permission(required_permissions):
    """
    Decorator to check for complex permission objects like:
    [{'subject': 'venue', 'action': 'read'}]
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_id = request.session.get("user_id")
            username = request.session.get("username")
            if not user_id:
                return JsonResponse({"error": "Authentication required."}, status=401)

            user_permissions = request.session.get("permissions", [])
            if username == "admin" or username == "ssp":
                return view_func(request, *args, **kwargs)
            # Match each required permission object
            for required in required_permissions:
                if required not in user_permissions:
                    return JsonResponse(
                        {"error": "Permission denied for action."},
                        status=403,
                    )

            return view_func(request, *args, **kwargs)

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

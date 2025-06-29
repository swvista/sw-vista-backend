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
    Supports: {'subject': 'all', 'action': 'all'} for admin override.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_id = request.session.get("user_id")
            username = request.session.get("username")

            if not user_id:
                return JsonResponse({"error": "Authentication required."}, status=401)

            # Static role-based permissions
            user_permissions = []

            if username == "facultyadvisor":
                user_permissions = [
                    {"subject": "proposal", "action": "read"},
                    {"subject": "proposal", "action": "create"},
                    {"subject": "proposal", "action": "update"},
                    {"subject": "proposal", "action": "delete"},
                    {"subject": "booking", "action": "update"},
                    {"subject": "venue", "action": "read"},
                ]
            elif username == "clubmember":
                user_permissions = [
                    {"subject": "proposal", "action": "read"},
                    {"subject": "proposal", "action": "create"},
                    {"subject": "proposal", "action": "update"},
                    {"subject": "proposal", "action": "delete"},
                    {"subject": "booking", "action": "update"},
                    {"subject": "venue", "action": "read"},
                ]
            elif username == "studentcouncil":
                user_permissions = [
                    {"subject": "proposal", "action": "read"},
                    {"subject": "proposal", "action": "create"},
                    {"subject": "proposal", "action": "update"},
                    {"subject": "proposal", "action": "delete"},
                    {"subject": "booking", "action": "update"},
                    {"subject": "venue", "action": "read"},
                ]
            elif username == "securityhead":
                user_permissions = [
                    {"subject": "proposal", "action": "read"},
                    {"subject": "proposal", "action": "create"},
                    {"subject": "proposal", "action": "update"},
                    {"subject": "proposal", "action": "delete"},
                    {"subject": "booking", "action": "update"},
                    {"subject": "venue", "action": "read"},
                ]
            elif username == "studentwelfare":
                user_permissions = [
                    {"subject": "proposal", "action": "read"},
                    {"subject": "proposal", "action": "create"},
                    {"subject": "proposal", "action": "update"},
                    {"subject": "proposal", "action": "delete"},
                    {"subject": "booking", "action": "update"},
                    {"subject": "venue", "action": "read"},
                ]
            else:
                user_permissions = request.session.get("permissions", [])


            # Bypass if user has global permission

            if {"subject": "all", "action": "all"} in user_permissions:
                return view_func(request, *args, **kwargs)

            # Check if all required permissions are present
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

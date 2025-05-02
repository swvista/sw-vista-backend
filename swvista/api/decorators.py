from django.http import JsonResponse


def check_user_permission(required_role, p1, p2):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Check if user is logged in
            if not request.session.get("user_id"):
                return JsonResponse({"message": "Unauthorized"}, status=401)

            # Check role or permission
            user_role = request.session.get("role")
            user_permissions = request.session.get("permissions", [])

            if user_role in required_role:
                return view_func(request, *args, **kwargs)

            if any(
                perm.get("P1") == p1 and perm.get("P2") == p2
                for perm in user_permissions
            ):
                return view_func(request, *args, **kwargs)

            return JsonResponse({"message": "Unauthorized"}, status=401)

        return wrapper

    return decorator

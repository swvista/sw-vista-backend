from functools import wraps

from django.http import JsonResponse

# Assuming you have a way to get the authenticated user from the request,
# e.g., request.user is an instance of your rbac.models.User
# If not, you'll need to adjust how 'user' is obtained.
# from .models import User # Might be needed depending on auth setup


def permission_required(*permissions):
    """
    Decorator to check if the request user has all the specified permissions.
    Relies on request.user being the authenticated rbac.models.User instance
    and the User model having the 'has_permission' method.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # --- Authentication/User Retrieval ---
            # Adjust this part based on how you get the authenticated user.
            # If using Django's auth, request.user might be Django's User,
            # not your rbac.models.User. You might need to fetch your
            # custom User based on request.user.id or similar.
            if not hasattr(request, "user") or not request.user.is_authenticated:
                # Or if request.user is not your custom User type
                return JsonResponse({"error": "Authentication required"}, status=401)

            user = request.user  # Assuming request.user *is* your rbac.models.User

            # --- Permission Check ---
            missing_permissions = []
            for perm_name in permissions:
                if not user.has_permission(perm_name):
                    missing_permissions.append(perm_name)

            if missing_permissions:
                return JsonResponse(
                    {
                        "error": "Permission denied.",
                        "required_permissions": permissions,
                        "missing_permissions": missing_permissions,
                    },
                    status=403,
                )

            # --- Execute View ---
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# Example Usage (in views.py):
#
# from .decorators import permission_required
# from .controller.user import create_user
#
# @csrf_exempt # If needed
# @permission_required('create_user_permission') # Use the actual permission name
# def user_create_view(request):
#     if request.method == 'POST':
#         return create_user(request)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)
#

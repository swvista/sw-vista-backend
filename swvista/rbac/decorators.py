from functools import wraps

from django.http import JsonResponse


def session_login_required(view_func):
    """
    Decorator to check if a user is logged in based on session data.
    Similar to @login_required, but uses our manual session key.
    """

    @wraps(view_func)  # Preserves original view function metadata
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return JsonResponse({"error": "Authentication required."}, status=401)
        # If logged in, proceed with the original view
        return view_func(request, *args, **kwargs)

    return _wrapped_view

import json

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from .controller.permission import (
    create_permission,
    delete_permission,
    get_permission,
    update_permission,
)
from .controller.role import (
    create_role,
    delete_role,
    get_role,
    get_role_permission,
    map_role_to_permission,
    unmap_role_permission,
    update_role,
)
from .controller.user import (
    create_user,
    delete_user,
    get_user,
    map_user_to_role,
    unmap_user_role,
    update_user,
)

# Import the custom decorator
from .decorators import session_login_required
from .models import Role, User, UserRole
from .serializers import UserRoleSerializer

# Create your views here.

# --- Authentication Views ---


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return JsonResponse(
                    {"error": "Username and password are required."}, status=400
                )

            try:
                user = User.objects.get(username=username)
                role = user.role

                # Get permission IDs or full permission list
                permission_ids = [
                    permission.id for permission in role.permissions.all()
                ]
                print("Permissions:", permission_ids)

                # get all permissions and sent as response
                if check_password(password, user.password):

                    # Manually create session data
                    request.session["user_id"] = user.id
                    request.session["username"] = user.username
                    # Optionally store role/permissions if needed frequently, but be mindful of session size
                    request.session["role"] = user.role.name
                    request.session["permissions"] = [
                        {"subject": permission.subject, "action": permission.action}
                        for permission in user.role.permissions.all()
                    ]

                    return JsonResponse(
                        {
                            "message": "Login successful.",
                            "user_id": user.id,
                            "username": user.username,
                            "role": role.id,
                            "permissions": permission_ids,
                        },
                        status=200,
                    )
                else:
                    return JsonResponse({"error": "Invalid credentials."}, status=401)
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid credentials."}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            # Log the exception e
            print(e)
            return JsonResponse(
                {"error": "An internal server error occurred."}, status=500
            )
    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)


@ensure_csrf_cookie
def logout_view(request):
    if request.method == "POST":
        try:
            request.session.flush()
            return JsonResponse({"message": "Logout successful."}, status=200)
        except Exception as e:
            # Log the exception e
            print(e)
            return JsonResponse(
                {"error": "An internal server error occurred during logout."},
                status=500,
            )
    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)


@ensure_csrf_cookie
def me_view(request):
    if request.method == "GET":
        user_id = request.session.get("user_id")
        print("request.session", request.session)
        print("user_id", user_id)
        if user_id:
            # User is logged in, retrieve info from session
            user_info = {
                "user_id": user_id,
                "username": request.session.get("username"),
                "role": request.session.get("role"),
                "permissions": request.session.get("permissions", []),
            }
            return JsonResponse(user_info, status=200)
        else:
            # User is not logged in
            return JsonResponse({"error": "Not authenticated"}, status=401)
    else:
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)


# --- Existing RBAC Views ---


@csrf_exempt
def index(request):
    if request.method == "POST":
        return JsonResponse({"message": "test POST"})
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
@session_login_required
def user(request):
    if request.method == "POST":
        return create_user(request)
    elif request.method == "GET":
        return get_user(request)
    elif request.method == "PUT":
        return update_user(request)
    elif request.method == "DELETE":
        return delete_user(request)
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
@session_login_required
def role(request):
    if request.method == "POST":
        return create_role(request)
    elif request.method == "GET":
        print("get role")
        return get_role(request)
    elif request.method == "PUT":
        return update_role(request)
    elif request.method == "DELETE":
        return delete_role(request)
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
@session_login_required
def permission(request):
    if request.method == "POST":
        return create_permission(request)
    elif request.method == "GET":
        return get_permission(request)
    elif request.method == "PUT":
        return update_permission(request)
    elif request.method == "DELETE":
        return delete_permission(request)
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
def user_role(request):
    if request.method == "POST":
        return map_user_to_role(request)
    elif request.method == "GET":
        return get_users_role(request)
    elif request.method == "DELETE":
        return unmap_user_role(request)
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
def role_permission(request):
    if request.method == "POST":
        return map_role_to_permission(request)
    elif request.method == "GET":
        return get_role_permission(request)
    elif request.method == "DELETE":
        return unmap_role_permission(request)
    else:
        return JsonResponse({"message": "test GET"})


def get_map_role_to_user(request):
    print("get map role to user")
    return map_role_to_permission(request)


@ensure_csrf_cookie
def get_users_role(request):
    if request.method == "GET":
        user_roles = UserRole.objects.all()
        print("user_roles")
        serializer = UserRoleSerializer(user_roles, many=True)
        print("serializer")
        print(serializer.data)

        all_users_data = []

        for user_role in user_roles:
            user = User.objects.get(id=user_role.user_id)
            role = Role.objects.get(id=user_role.role_id)
            all_users_data.append(
                {
                    "username": user.username,
                    "email": user.email,
                    "role": {
                        "id": role.id,
                        "name": role.name,
                        "description": role.description,
                        "permissions": [
                            {"id": permission.id, "name": permission.name}
                            for permission in role.permissions.all()
                        ],
                    },
                }
            )

        return JsonResponse(all_users_data, safe=False, status=200)
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
def get_user_role_by_user_id(request, user_id):
    if request.method == "GET":
        user_role = UserRole.objects.get(user_id=user_id)
        user = User.objects.get(id=user_id)
        role = Role.objects.get(id=user_role.role_id)
        user_role_data = {
            "username": user.username,
            "email": user.email,
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": [
                    {"id": permission.id, "name": permission.name}
                    for permission in role.permissions.all()
                ],
            },
        }
        return JsonResponse(user_role_data, safe=False, status=200)
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
def get_user_role_by_role_id(request, role_id):
    if request.method == "GET":
        user_role = UserRole.objects.get(role_id=role_id)
        user = User.objects.get(id=user_role.user_id)
        role = Role.objects.get(id=role_id)
        user_role_data = {
            "username": user.username,
            "email": user.email,
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": [
                    {"id": permission.id, "name": permission.name}
                    for permission in role.permissions.all()
                ],
            },
        }
        return JsonResponse(user_role_data, safe=False, status=200)
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
def get_user_role_by_user_id_and_role_id(request, user_id, role_id):
    if request.method == "GET":
        user_role = UserRole.objects.get(user_id=user_id, role_id=role_id)
        serializer = UserRoleSerializer(user_role)
        return JsonResponse(serializer.data, status=200)
    else:
        return JsonResponse({"message": "test GET"})

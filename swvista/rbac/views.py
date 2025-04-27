from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from .controller.permission import (
    create_permission,
    delete_permission,
    get_permission,
    update_permission,
)
from .controller.relationship import (
    map_role_to_permission,
    map_user_to_role,
    unmap_role_permission,
    unmap_user_role,
)
from .controller.role import (
    create_role,
    delete_role,
    get_role,
    get_role_permission,
    update_role,
)
from .controller.user import create_user, delete_user, get_user, update_user
from .models import UserRole
from .serializers import UserRoleSerializer

# Create your views here.


@ensure_csrf_cookie
def index(request):
    if request.method == "POST":
        return JsonResponse({"message": "test POST"})
    else:
        return JsonResponse({"message": "test GET"})


@ensure_csrf_cookie
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


def user_role(request):
    if request.method == "POST":
        return map_user_to_role(request)
    elif request.method == "GET":
        return get_users_role(request)
    elif request.method == "DELETE":
        return unmap_user_role(request)
    else:
        return JsonResponse({"message": "test GET"})


def role_permission(request):
    if request.method == "POST":
        return map_role_to_permission(request)
    elif request.method == "GET":
        return get_role_permission(request)
    elif request.method == "DELETE":
        return unmap_role_permission(request)
    else:
        return JsonResponse({"message": "test GET"})


def get_users_role(request):
    if request.method == "GET":
        user_roles = UserRole.objects.all()
        serializer = UserRoleSerializer(user_roles, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "test GET"})


def get_user_role_by_user_id(request, user_id):
    if request.method == "GET":
        user_role = UserRole.objects.get(user_id=user_id)
        serializer = UserRoleSerializer(user_role)
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "test GET"})


def get_user_role_by_role_id(request, role_id):
    if request.method == "GET":
        user_role = UserRole.objects.get(role_id=role_id)
        serializer = UserRoleSerializer(user_role)
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "test GET"})


def get_user_role_by_user_id_and_role_id(request, user_id, role_id):
    if request.method == "GET":
        user_role = UserRole.objects.get(user_id=user_id, role_id=role_id)
        serializer = UserRoleSerializer(user_role)
        return JsonResponse(serializer.data, status=200)
    else:
        return JsonResponse({"message": "test GET"})

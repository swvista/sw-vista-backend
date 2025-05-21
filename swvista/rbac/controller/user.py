import json

from django.http import JsonResponse

from ..decorators import check_user_permission, session_login_required
from ..models import User, UserRole
from ..serializers import UserRoleSerializer, UserSerializer


@session_login_required
@check_user_permission([{"subject": "user", "action": "create"}])
def create_user(request):
    body = json.loads(request.body)
    serializer = UserSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@session_login_required
@check_user_permission([{"subject": "user", "action": "read"}])
def get_user(request):

    all_users = User.objects.all()
    all_users_data = []
    for user in all_users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
                "description": user.role.description,
                "permissions": [
                    {"id": permission.id, "name": permission.name}
                    for permission in user.role.permissions.all()
                ],
            },
        }
        all_users_data.append(user_data)
    return JsonResponse(all_users_data, safe=False, status=200)


@session_login_required
@check_user_permission([{"subject": "user", "action": "update"}])
def update_user(request):
    body = json.loads(request.body)
    user = User.objects.get(id=body["id"])
    serializer = UserSerializer(user, data=body)
    if serializer.is_valid():
        serializer.save()
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
                "description": user.role.description,
                "permissions": [
                    {"id": permission.id, "name": permission.name}
                    for permission in user.role.permissions.all()
                ],
            },
        }
        return JsonResponse(user_data, status=200)
    return JsonResponse(serializer.errors, status=400)


@session_login_required
@check_user_permission([{"subject": "user", "action": "delete"}])
def delete_user(request):
    body = json.loads(request.body)
    user = User.objects.get(id=int(body["id"]))
    print(user)
    if user:
        user.delete()
        return JsonResponse({"message": "User deleted successfully"}, status=200)
    else:
        return JsonResponse({"message": "User not found"}, status=404)


@session_login_required
@check_user_permission([{"subject": "user", "action": "write"}])
def map_user_to_role(request):
    body = json.loads(request.body)
    print(body)
    serializer = UserRoleSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@session_login_required
@check_user_permission([{"subject": "user", "action": "write"}])
def unmap_user_role(request):
    body = json.loads(request.body)
    print(body)
    user_role = UserRole.objects.get(id=body["id"])
    user_role.delete()
    return JsonResponse({"message": "User role deleted successfully"}, status=200)

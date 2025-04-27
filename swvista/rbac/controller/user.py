import json

from django.http import JsonResponse

from ..models import User, UserRole
from ..serializers import UserRoleSerializer, UserSerializer


def create_user(request):
    body = json.loads(request.body)
    serializer = UserSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


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


def update_user(request):
    body = json.loads(request.body)
    user = User.objects.get(id=body["id"])
    serializer = UserSerializer(user, data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=200)
    return JsonResponse(serializer.errors, status=400)


def delete_user(request):
    user = User.objects.get(id=request.body["id"])
    user.delete()
    return JsonResponse({"message": "User deleted successfully"}, status=200)


def map_user_to_role(request):
    body = json.loads(request.body)
    print(body)
    serializer = UserRoleSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


def unmap_user_role(request):
    body = json.loads(request.body)
    print(body)
    user_role = UserRole.objects.get(id=body["id"])
    user_role.delete()
    return JsonResponse({"message": "User role deleted successfully"}, status=200)

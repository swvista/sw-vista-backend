import json

from django.http import JsonResponse

from ..models import RolePermission, UserRole
from ..serializers import RolePermissionSerializer, UserRoleSerializer


def map_user_to_role(request):
    body = json.loads(request.body)
    print(body)
    serializer = UserRoleSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


def map_role_to_permission(request):
    body = json.loads(request.body)
    print(body)
    serializer = RolePermissionSerializer(data=body)
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


def unmap_role_permission(request):
    body = json.loads(request.body)
    print(body)
    role_permission = RolePermission.objects.get(id=body["id"])
    role_permission.delete()
    return JsonResponse({"message": "Role permission deleted successfully"}, status=200)

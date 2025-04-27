import json

from django.http import JsonResponse

from ..models import Role, RolePermission
from ..serializers import RolePermissionSerializer, RoleSerializer


def create_role(request):
    body = json.loads(request.body)
    serializer = RoleSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


def get_role(request):
    roles = Role.objects.all()
    all_roles_data = []
    for role in roles:
        role_data = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": [
                {"id": permission.id, "name": permission.name}
                for permission in role.permissions.all()
            ],
        }
        all_roles_data.append(role_data)

    return JsonResponse(all_roles_data, safe=False, status=200)


def update_role(request):
    body = json.loads(request.body)
    role = Role.objects.get(id=body["id"])
    if role:
        serializer = RoleSerializer(role, data=body)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    else:
        return JsonResponse({"message": "Role not found"}, status=404)


def delete_role(request):
    role = Role.objects.get(id=request.body["id"])
    if role:
        role.delete()
        return JsonResponse({"message": "Role deleted successfully"}, status=200)
    else:
        return JsonResponse({"message": "Role not found"}, status=404)


def get_role_permission(request):
    role = Role.objects.get(id=request.body["id"])
    if role:
        serializer = RolePermissionSerializer(role, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "Role not found"}, status=404)


def unmap_role_permission(request):
    body = json.loads(request.body)
    print(body)
    role_permission = RolePermission.objects.get(id=body["id"])
    role_permission.delete()
    return JsonResponse({"message": "Role permission deleted successfully"}, status=200)


def map_role_to_permission(request):
    body = json.loads(request.body)
    print(body)
    serializer = RolePermissionSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)

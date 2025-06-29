import json

from django.http import JsonResponse

from ..decorators import check_user_permission, session_login_required
from ..models import Role, RolePermission
from ..serializers import RolePermissionSerializer, RoleSerializer


# @check_user_permission([{"subject": "role", "action": "create"}])
def create_role(request):
    body = json.loads(request.body)
    serializer = RoleSerializer(data=body)
    if serializer.is_valid():
        role_instance = serializer.save()
        role_data = {
            "id": role_instance.id,
            "name": role_instance.name,
            "description": role_instance.description,
            "permissions": [
                {
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                }
                for permission in role_instance.permissions.all()
            ],
        }
        return JsonResponse(role_data, status=201)
    return JsonResponse(serializer.errors, status=400)


# @check_user_permission([{"subject": "role", "action": "read"}])
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


# @check_user_permission([{"subject": "role", "action": "update"}])
def update_role(request):
    body = json.loads(request.body)
    role = Role.objects.get(id=body["id"])
    if role:
        serializer = RoleSerializer(role, data=body)
        if serializer.is_valid():
            role_instance = serializer.save()
            role_data = {
                "id": role_instance.id,
                "name": role_instance.name,
                "description": role_instance.description,
                "permissions": [
                    {
                        "id": permission.id,
                        "name": permission.name,
                        "description": permission.description,
                    }
                    for permission in role_instance.permissions.all()
                ],
            }
            return JsonResponse(role_data, status=200)
        return JsonResponse(serializer.errors, status=400)
    else:
        return JsonResponse({"message": "Role not found"}, status=404)


# @check_user_permission([{"subject": "role", "action": "delete"}])
def delete_role(request):
    body = json.loads(request.body)
    role = Role.objects.get(id=body["id"])
    if role:
        # Store data before deletion
        deleted_role_data = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": [
                {
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                }
                for permission in role.permissions.all()  # Access permissions BEFORE deleting
            ],
        }
        deleted_count, _ = role.delete()  # role.delete() returns a tuple
        if deleted_count > 0:  # Check if deletion was successful
            return JsonResponse(deleted_role_data, status=200)
        else:
            return JsonResponse(
                {"message": "Role not deleted"}, status=400
            )  # Should likely be different status/error
    else:
        # This 'else' might be redundant if .get() raises DoesNotExist
        return JsonResponse({"message": "Role not found"}, status=404)


# @check_user_permission([{"subject": "role", "action": "read"}])
def get_role_permission(request):
    body = json.loads(request.body)
    role = Role.objects.get(id=body["id"])
    if role:
        serializer = RolePermissionSerializer(role, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse({"message": "Role not found"}, status=404)


# @check_user_permission([{"subject": "role", "action": "write"}])
def unmap_role_permission(request):
    body = json.loads(request.body)
    print(body)
    role_permission = RolePermission.objects.get(id=body["id"])
    role_permission.delete()
    return JsonResponse({"message": "Role permission deleted successfully"}, status=200)


# @check_user_permission([{"subject": "role", "action": "write"}])
def map_role_to_permission(request):
    body = json.loads(request.body)
    print(body)
    serializer = RolePermissionSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)

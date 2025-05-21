import json

from django.http import JsonResponse

from ..decorators import check_user_permission, session_login_required
from ..models import Permission
from ..serializers import PermissionSerializer


@session_login_required
@check_user_permission([{"subject": "permission", "action": "create"}])
def create_permission(request):
    body = json.loads(request.body)
    serializer = PermissionSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@session_login_required
@check_user_permission([{"subject": "permission", "action": "read"}])
def get_permission(request):
    permissions = Permission.objects.all()
    serializer = PermissionSerializer(permissions, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)


@session_login_required
@check_user_permission([{"subject": "permission", "action": "update"}])
def update_permission(request):
    body = json.loads(request.body)
    permission = Permission.objects.get(id=body["id"])
    serializer = PermissionSerializer(permission, data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=200)
    return JsonResponse(serializer.errors, status=400)


@session_login_required
@check_user_permission([{"subject": "permission", "action": "delete"}])
def delete_permission(request):
    body = json.loads(request.body)
    permission = Permission.objects.get(id=body["id"])
    if permission:
        permission_data = {
            "id": permission.id,
            "name": permission.name,
            "description": permission.description,
        }
        permission.delete()
        return JsonResponse(permission_data, status=200)
    else:
        return JsonResponse({"message": "Permission not found"}, status=404)

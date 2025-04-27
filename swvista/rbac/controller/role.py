import json

from django.http import JsonResponse

from ..models import Role
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
    serializer = RoleSerializer(roles, many=True)
    print(serializer.data)
    if serializer.is_valid():
        return JsonResponse(serializer.data, safe=False, status=200)
    else:
        return JsonResponse(serializer.errors, status=400)


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

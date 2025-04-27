import json

from django.http import JsonResponse

from ..models import Permission
from ..serializers import PermissionSerializer


def create_permission(request):
    body = json.loads(request.body)
    serializer = PermissionSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


def get_permission(request):
    permissions = Permission.objects.all()
    serializer = PermissionSerializer(permissions, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)


def update_permission(request):
    body = json.loads(request.body)
    permission = Permission.objects.get(id=body["id"])
    serializer = PermissionSerializer(permission, data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=200)
    return JsonResponse(serializer.errors, status=400)


def delete_permission(request):
    permission = Permission.objects.get(id=request.body["id"])
    if permission:
        permission.delete()
        return JsonResponse({"message": "Permission deleted successfully"}, status=200)
    else:
        return JsonResponse({"message": "Permission not found"}, status=404)

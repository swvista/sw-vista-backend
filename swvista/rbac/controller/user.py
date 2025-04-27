import json

from django.http import JsonResponse

from ..models import User
from ..serializers import UserSerializer


def create_user(request):
    body = json.loads(request.body)
    serializer = UserSerializer(data=body)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


def get_user(request):
    all_users = User.objects.all()
    serializer = UserSerializer(all_users, many=True)

    return JsonResponse(serializer.data, safe=False, status=200)


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

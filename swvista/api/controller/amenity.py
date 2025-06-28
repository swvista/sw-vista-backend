import json

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from ..models.amenity import Amenity
from ..serializers import AmenitySerializer


@require_http_methods(["POST"])
@ensure_csrf_cookie
def create_amenity(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)

    name = data.get("name")
    description = data.get("description")
    if not name or not description:
        return JsonResponse(
            {"message": "Both name and description are required"}, status=400
        )

    amenity = Amenity.objects.create_amenity(name=name, description=description)
    return JsonResponse(AmenitySerializer(amenity).data, status=201)


@require_http_methods(["GET"])
@ensure_csrf_cookie
def list_amenities(request):
    qs = Amenity.objects.list_amenities()
    serializer = AmenitySerializer(qs, many=True)
    return JsonResponse(serializer.data, status=200, safe=False)


@require_http_methods(["GET"])
@ensure_csrf_cookie
def get_amenity(request, id):
    try:
        amenity = Amenity.objects.get_amenity(id=id)
    except Amenity.DoesNotExist:
        return JsonResponse({"message": "Amenity not found"}, status=404)
    serializer = AmenitySerializer(amenity)
    return JsonResponse(serializer.data, status=200)


@require_http_methods(["PUT"])
@ensure_csrf_cookie
def update_amenity(request, id):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)

    try:
        amenity = Amenity.objects.update_amenity(id=id, **data)
    except Amenity.DoesNotExist:
        return JsonResponse({"message": "Amenity not found"}, status=404)

    serializer = AmenitySerializer(amenity)
    return JsonResponse(serializer.data, status=200)


@require_http_methods(["DELETE"])
@ensure_csrf_cookie
def delete_amenity(request, id):
    try:
        Amenity.objects.delete_amenity(id=id)
    except Amenity.DoesNotExist:
        return JsonResponse({"message": "Amenity not found"}, status=404)

    return JsonResponse({"message": "Amenity deleted"}, status=200)

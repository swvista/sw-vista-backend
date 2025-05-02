import json

from api.models import Venue
from api.serializers import VenueSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rbac.constants import roles

from ..decorators import check_user_permission

# Controllers might be redundant, but they are useful for testing and development.


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "read")
def get_all_venues(request):
    venues = Venue.objects.all()
    serializer = VenueSerializer(venues, many=True)
    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "read")
def get_venue_by_id(request, id):
    try:
        venue = get_object_or_404(Venue, id=id)
        serializer = VenueSerializer(venue)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


@require_http_methods(["POST"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "write")
def create_venue(request):
    try:
        data = json.loads(request.body)
        serializer = VenueSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)


@require_http_methods(["PUT"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "write")
def update_venue(request, id):
    venue = get_object_or_404(Venue, id=id)
    try:
        data = json.loads(request.body)
        serializer = VenueSerializer(venue, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=400)


@require_http_methods(["DELETE"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "delete")
def delete_venue(request, id):
    venue = get_object_or_404(Venue, id=id)
    venue.delete()
    return JsonResponse({"message": "Venue deleted successfully"}, status=200)

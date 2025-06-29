import json

from api.models.amenity import Amenity
from api.models.venue import Venue
from api.models.VenueAmenities import VenueAmenities
from api.serializers import VenueAmenitiesSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

# 📍 Add your decorators for authentication/permissions
# from ..decorators import check_user_permission


@require_http_methods(["POST"])
@ensure_csrf_cookie
def add_venue_amenity(request, venue_id):
    """
    POST /api/venues/?venue_id=<id>
    Body: { "amenity_id": X }
    """
    try:
        payload = json.loads(request.body)
        amenity_id = payload["amenity_id"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"message": "Invalid or missing 'amenity_id'"}, status=400)

    try:
        venue = get_object_or_404(Venue, id=venue_id)
    except Exception:
        return JsonResponse({"message": "venue not found"})

    try:

        amenity = get_object_or_404(Amenity, id=amenity_id)
    except Exception:
        return JsonResponse({"message": "amenity not found"})
    va = VenueAmenities.objects.add_amenity(venue.id, amenity.id)
    serializer = VenueAmenitiesSerializer(va)

    return JsonResponse(serializer.data, status=201)


@require_http_methods(["GET"])
@ensure_csrf_cookie
def list_venue_amenities(request, venue_id):
    """
    GET /api/venues/<venue_id>/amenities/
    """
    get_object_or_404(Venue, id=venue_id)
    queryset = VenueAmenities.objects.list_for_venue(venue_id)
    serializer = VenueAmenitiesSerializer(queryset, many=True)
    return JsonResponse(serializer.data, status=200, safe=False)


@require_http_methods(["DELETE"])
@ensure_csrf_cookie
def remove_venue_amenity(request, venue_id, amenity_id):
    """
    DELETE /api/venues/<venue_id>/amenities/<amenity_id>/
    """
    get_object_or_404(Venue, id=venue_id)
    get_object_or_404(Amenity, id=amenity_id)

    try:
        VenueAmenities.objects.remove_amenity(venue_id, amenity_id)
        return JsonResponse({"message": "Amenity removed from venue."}, status=200)
    except VenueAmenities.DoesNotExist:
        return JsonResponse({"message": "Association not found."}, status=404)


@require_http_methods(["PUT"])
@ensure_csrf_cookie
def update_venue_amenity(request, venue_id, old_amenity_id):
    """
    PUT /api/venues/<venue_id>/amenities/<old_amenity_id>/
    Body: { "new_amenity_id": Y }
    """
    get_object_or_404(Venue, id=venue_id)
    get_object_or_404(Amenity, id=old_amenity_id)

    try:
        payload = json.loads(request.body)
        new_amenity_id = payload["new_amenity_id"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse(
            {"message": "Invalid or missing 'new_amenity_id'"}, status=400
        )

    new_amenity = get_object_or_404(Amenity, id=new_amenity_id)

    try:
        va = VenueAmenities.objects.update_amenity(
            venue_id, old_amenity_id, new_amenity.id
        )
        serializer = VenueAmenitiesSerializer(va)
        return JsonResponse(serializer.data, status=200)
    except VenueAmenities.DoesNotExist:
        return JsonResponse({"message": "Original association not found."}, status=404)

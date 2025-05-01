import json

from api.models import Venue
from api.serializers import VenueSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rbac.constants import roles


def check_user_permission(request, role, p1, p2):
    if not request.session.get("user_id"):
        return JsonResponse({"message": "Unauthorized"}, status=401)

    # Allow if user has the required role
    if request.session.get("role") == role:
        return None

    # Allow if user has the required P1/P2 permission
    user_permissions = request.session.get("permissions", [])
    if any(perm.get("P1") == p1 and perm.get("P2") == p2 for perm in user_permissions):
        return None

    # If neither, deny access
    return JsonResponse({"message": "Unauthorized"}, status=401)


@csrf_exempt
def venue(request):
    if request.method == "GET":
        check = check_user_permission(request, roles["admin"], "venue", "read")
        if check is not None:
            return check

        venues = Venue.objects.all()
        id = request.GET.get("id")
        name = request.GET.get("name")
        address = request.GET.get("address")
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")

        if id:
            venues = venues.filter(id=id)
        if name:
            venues = venues.filter(name__icontains=name)
        if address:
            venues = venues.filter(address__icontains=address)
        if latitude:
            venues = venues.filter(latitude=latitude)
        if longitude:
            venues = venues.filter(longitude=longitude)

        # If no venues are found
        if not venues:
            return JsonResponse({"message": "No venues found"}, status=404)

        # Serialize and return venues
        serializer = VenueSerializer(venues, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == "POST":
        # Handle POST request
        check = check_user_permission(request, roles["admin"], "venue", "write")
        if check:
            return check
        try:
            data = json.loads(request.body)
            serializer = VenueSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    elif request.method == "PUT":
        # Handle PUT request for updating a venue
        check = check_user_permission(request, roles["admin"], "venue", "write")
        if check:
            return check
        try:
            body = json.loads(request.body)
            venue = get_object_or_404(Venue, id=body["id"])
            serializer = VenueSerializer(venue, data=body)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)
        except KeyError:
            return JsonResponse(
                {"message": "ID is required for updating a venue"}, status=400
            )
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    elif request.method == "DELETE":
        # Handle DELETE request
        check = check_user_permission(request, roles["admin"], "venue", "delete")
        if check:
            return check
        try:
            body = json.loads(request.body)
            venue = get_object_or_404(Venue, id=body["id"])
            venue.delete()
            return JsonResponse({"message": "Venue deleted successfully"}, status=200)
        except KeyError:
            return JsonResponse(
                {"message": "ID is required to delete a venue"}, status=400
            )
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)


@csrf_exempt
def get_venue_by_id(request, id):
    if request.method == "GET":
        check = check_user_permission(request, roles["admin"], "venue", "read")
        if check is not None:
            return JsonResponse({"message": "Unauthorized"}, status=401)
        venue = get_object_or_404(Venue, id=id)
        serializer = VenueSerializer(venue)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)

import json

# api.models and api.serializers suggests these might be in a different app
# Adjust the import path if 'api' is the same app as these views
from api.models import Venue
from api.serializers import VenueSerializer
from django.http import JsonResponse  # Import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rbac.constants import roles

# Assuming the decorators module is one level up from the current views file
from ..decorators import check_user_permission

# Note on Controllers: In Django's MVT pattern, these view functions often act
# as the "Controller" logic. They handle the request, interact with models,
# and return responses, often using serializers for data transformation.


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "read")
def get_all_venues(request):
    """
    Retrieves a list of all venues.
    Requires 'read' permission on 'venue'.
    """
    venues = Venue.objects.all()
    # Consider pagination here if the number of venues can be large
    # from django.core.paginator import Paginator
    # paginator = Paginator(venues, 25) # Example: 25 venues per page
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    # serializer = VenueSerializer(page_obj, many=True)
    serializer = VenueSerializer(venues, many=True)
    # safe=False is required because the top-level object is a list
    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "read")
def get_venue_by_id(request, id):
    """
    Retrieves a single venue by its ID.
    Requires 'read' permission on 'venue'.
    Returns 404 if the venue is not found.
    """
    # get_object_or_404 handles the DoesNotExist exception and raises Http404
    venue = get_object_or_404(Venue, id=id)
    serializer = VenueSerializer(venue)
    # safe=False is not strictly needed for a single object (dict), but harmless
    return JsonResponse(serializer.data, safe=False)
    # Removed the broad try...except Exception as get_object_or_404 handles the primary error case (not found).
    # Let other unexpected errors propagate for standard Django error handling/logging.


@require_http_methods(["POST"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "write")
def create_venue(request):
    """
    Creates a new venue.
    Requires 'write' permission on 'venue'.
    Expects venue data in JSON format in the request body.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "Invalid JSON format in request body"}, status=400
        )

    # If the Venue needs to be associated with the user creating it:
    # user_id = request.session.get("user_id")
    # if not user_id:
    #     return JsonResponse({"message": "Authentication required."}, status=401)
    # try:
    #     current_user = User.objects.get(id=user_id) # Make sure User model is imported
    # except User.DoesNotExist:
    #     return JsonResponse({"message": "User not found."}, status=404)
    # serializer = VenueSerializer(data=data)
    # if serializer.is_valid():
    #     # Pass the user instance if the serializer/model expects it
    #     serializer.save(created_by=current_user) # Or appropriate field name
    #     return JsonResponse(serializer.data, status=201)
    # else:
    #     return JsonResponse(serializer.errors, status=400)

    # --- Code assuming Venue does NOT need automatic user association ---
    serializer = VenueSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)  # 201 Created
    else:
        # Return validation errors from the serializer
        return JsonResponse(serializer.errors, status=400)  # 400 Bad Request


@require_http_methods(["PUT"])  # Or ["PUT", "PATCH"] if using partial=True below
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "write")
def update_venue(request, id):
    """
    Updates an existing venue by its ID.
    Requires 'write' permission on 'venue'.
    Expects updated venue data in JSON format in the request body.
    Returns 404 if the venue is not found.
    """
    venue = get_object_or_404(Venue, id=id)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "Invalid JSON format in request body"}, status=400
        )

    # Use partial=True if you want to support PATCH (partial updates)
    # serializer = VenueSerializer(venue, data=data, partial=True)
    serializer = VenueSerializer(venue, data=data)  # Assumes PUT (full update)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=200)  # 200 OK
    else:
        # Return validation errors
        return JsonResponse(serializer.errors, status=400)  # 400 Bad Request


@require_http_methods(["DELETE"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "venue", "delete")
def delete_venue(request, id):
    """
    Deletes a venue by its ID.
    Requires 'delete' permission on 'venue'.
    Returns 404 if the venue is not found.
    """
    venue = get_object_or_404(Venue, id=id)
    venue.delete()
    # Return 200 OK with message, or 204 No Content
    return JsonResponse({"message": "Venue deleted successfully"}, status=200)
    # Alternatively, for 204 No Content:
    # from django.http import HttpResponse
    # return HttpResponse(status=204)

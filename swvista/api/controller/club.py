import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rbac.models import User  # Assuming User model is in rbac app

from ..models.club import Club
from ..models.club_members import ClubMember

# Adjust import paths based on your project structure
from ..serializers import ClubMemberSerializer, ClubSerializer

# Consider adding permission decorators (like check_user_permission)
# from ..decorators import check_user_permission
# from rbac.constants import roles

# ----- Club Views -----


@require_http_methods(["POST"])
@ensure_csrf_cookie
# Example permission: @check_user_permission([roles["admin"]], "club", "write")
def create_club(request):
    """
    Creates a new Club.
    Requires appropriate write permissions.
    Expects JSON data for the club in the request body.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "Invalid JSON format in request body."}, status=400
        )

    # Optionally associate the creator if your model/serializer expects it
    # user_id = request.session.get("user_id")
    # if user_id:
    #    creator = get_object_or_404(User, id=user_id)
    #    # Modify save call below: serializer.save(creator=creator)
    # else:
    #    return JsonResponse({"message": "Authentication required to create a club."}, status=401)

    serializer = ClubSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)  # 201 Created
    else:
        return JsonResponse(serializer.errors, status=400)  # 400 Bad Request


@require_http_methods(["GET"])
@ensure_csrf_cookie
# Example permission: @check_user_permission([roles["admin"], roles["user"]], "club", "read")
def get_all_clubs(request):
    """
    Retrieves a list of all clubs.
    Requires appropriate read permissions.
    Consider adding pagination for large datasets.
    """
    clubs = Club.objects.all()
    serializer = ClubSerializer(clubs, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)  # safe=False for list


@require_http_methods(["GET"])
@ensure_csrf_cookie
# Example permission: @check_user_permission([roles["admin"], roles["user"]], "club", "read")
def get_club_by_id(request, id):
    """
    Retrieves a single club by its ID.
    Requires appropriate read permissions.
    Returns 404 if the club is not found.
    """
    club = get_object_or_404(Club, id=id)
    serializer = ClubSerializer(club)
    return JsonResponse(serializer.data, status=200)


@require_http_methods(["PUT"])  # Use PUT for full updates
@ensure_csrf_cookie
# Example permission: @check_user_permission([roles["admin"]], "club", "write")
def update_club(request, id):
    """
    Updates an existing club by its ID.
    Requires appropriate write permissions.
    Expects complete JSON data for the club in the request body.
    Returns 404 if the club is not found.
    (For partial updates, use PATCH and serializer(..., partial=True))
    """
    club = get_object_or_404(Club, id=id)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "Invalid JSON format in request body."}, status=400
        )

    serializer = ClubSerializer(club, data=data)  # Pass existing instance
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=200)  # 200 OK
    else:
        return JsonResponse(serializer.errors, status=400)  # 400 Bad Request


@require_http_methods(["DELETE"])
@ensure_csrf_cookie
# Example permission: @check_user_permission([roles["admin"]], "club", "delete")
def delete_club(request, id):
    """
    Deletes a club by its ID.
    Requires appropriate delete permissions.
    Prevents deletion if the club has members.
    Returns 404 if the club is not found.
    """
    club = get_object_or_404(Club, id=id)

    # Check if the club has any members (efficiently)
    if ClubMember.objects.filter(club=club).exists():
        return JsonResponse(
            {"message": "Club cannot be deleted because it has members."},
            status=400,  # 400 Bad Request (or 409 Conflict)
        )

    club.delete()
    return JsonResponse({"message": "Club deleted successfully."}, status=200)  # 200 OK
    # Or return HttpResponse(status=204) for No Content


# ----- Club Member Views -----


@require_http_methods(["POST"])
@ensure_csrf_cookie
# Example permission: @check_user_permission([roles["admin"]], "club_member", "write") # Or more specific permission
def add_member_to_club(request, id):
    """
    Adds a user as a member to a specific club (by club ID in URL).
    Requires appropriate permissions.
    Expects JSON like {"user": user_id, "role": "optional_role", ...} in body.
    Returns 404 if club or specified user not found.
    Returns 400 if user is already a member or data is invalid.
    """
    club = get_object_or_404(Club, id=id)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "Invalid JSON format in request body."}, status=400
        )

    user_id = data.get("user")
    if user_id is None:
        # Mimic serializer validation error format
        return JsonResponse({"user": ["This field is required."]}, status=400)

    # Validate user existence before checking membership or serializing
    user = get_object_or_404(User, id=user_id)

    # Prevent adding duplicate memberships
    if ClubMember.objects.filter(club=club, user=user).exists():
        return JsonResponse(
            {"message": "User is already a member of this club."}, status=400
        )

    # Ensure the serializer receives the correct club ID from the URL path
    data["club"] = club.id

    serializer = ClubMemberSerializer(data=data)
    if serializer.is_valid():
        # The serializer should handle associating the user_id and club_id
        serializer.save()
        return JsonResponse(serializer.data, status=201)  # 201 Created
    else:
        return JsonResponse(serializer.errors, status=400)  # 400 Bad Request


@require_http_methods(["POST"])  # Or DELETE to /api/clubs/{club_id}/members/{user_id}/
@ensure_csrf_cookie
# Example permission: @check_user_permission([roles["admin"]], "club_member", "delete") # Or user themselves
def remove_member_from_club(request):
    """
    Removes a user from a club.
    Requires appropriate permissions.
    Expects JSON like {"club_id": club_id, "user_id": user_id} in the request body.
    Returns 404 if club, user, or membership not found.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON format"}, status=400)

    club_id = data.get("club_id")
    user_id = data.get("user_id")

    if not club_id or not user_id:
        return JsonResponse(
            {
                "message": "Both 'club_id' and 'user_id' are required in the request body."
            },
            status=400,
        )

    # Find the specific membership record using get_object_or_404 for clarity
    membership = get_object_or_404(ClubMember, club_id=club_id, user_id=user_id)

    # If get_object_or_404 succeeds, the membership exists. Delete it.
    membership.delete()
    return JsonResponse(
        {"message": "Member removed from club successfully."}, status=200
    )  # 200 OK
    # Or return HttpResponse(status=204) for No Content


@require_http_methods(["GET"])
@ensure_csrf_cookie
# Example permission: @check_user_permission([roles["admin"], roles["user"]], "club_member", "read") # Or just club members
def get_all_members_of_club(request, id):
    """
    Retrieves a list of all members (ClubMember details) for a specific club.
    Requires appropriate read permissions.
    Returns 404 if the club is not found.
    """
    club = get_object_or_404(Club, id=id)
    # Consider optimization: .select_related('user') if User details are nested in serializer
    memberships = ClubMember.objects.filter(club=club)
    serializer = ClubMemberSerializer(memberships, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)  # safe=False for list


@require_http_methods(["GET"])
@ensure_csrf_cookie
# No specific permission check needed here, relies on authentication below
def get_my_clubs(request):
    """
    Retrieves a list of club memberships for the currently authenticated user.
    Returns 401 if the user is not authenticated.
    Returns 404 if the authenticated user doesn't exist in DB.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse(
            {"message": "Authentication required."}, status=401
        )  # 401 Unauthorized

    # Verify the user from the session exists
    user = get_object_or_404(User, id=user_id)

    # Retrieve the ClubMember records associated with this user
    # Consider optimization: .select_related('club') if Club details are nested in serializer
    memberships = ClubMember.objects.filter(user=user)
    # Note: This serializes the *membership* records (role, join date, etc.),
    # potentially including nested club/user info depending on the serializer config.
    serializer = ClubMemberSerializer(memberships, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)  # safe=False for list

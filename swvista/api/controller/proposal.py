import json

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rbac.constants import roles
from rbac.models import User

from ..decorators import check_user_permission
from ..models.proposal import Proposal
from ..serializers import ProposalSerializer

# UserSerializer is removed as it's not directly used in these views
# It might be used within ProposalSerializer, which is imported


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "read")
def get_all_proposals_by_user(request):
    # Retrieve user ID from session
    user_id = request.session.get("user_id")
    if not user_id:
        # Return 401 if user is not authenticated
        return JsonResponse({"message": "Authentication required."}, status=401)
    try:
        # Get the user object based on the ID
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # Return 404 if the user associated with the session ID doesn't exist
        return JsonResponse({"message": "User not found."}, status=404)
    # Filter proposals for the specific user
    proposals = Proposal.objects.filter(user=user)
    serializer = ProposalSerializer(proposals, many=True)
    # Use safe=False for list serialization
    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "read")
def get_all_proposals(request):
    # Retrieve all proposal objects
    proposals = Proposal.objects.all()
    serializer = ProposalSerializer(proposals, many=True)
    # Use safe=False for list serialization
    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["GET"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "read")
def get_proposal_by_id(request, id):
    try:
        # Retrieve a specific proposal by its ID
        proposal = Proposal.objects.get(id=id)
    except Proposal.DoesNotExist:
        # Return 404 if the proposal with the given ID is not found
        return JsonResponse({"message": "Proposal not found."}, status=404)
    serializer = ProposalSerializer(proposal)
    # safe=False is not strictly necessary for single object serialization but doesn't hurt
    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["POST"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "write")
def create_proposal(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body)
    except json.JSONDecodeError:
        # Return 400 if the request body is not valid JSON
        return JsonResponse({"message": "Invalid JSON format"}, status=400)

    # Prevent users from setting a status during creation
    # Assumes 'status' field might exist and should not be set initially
    if data.get("status"):  # Check if 'status' key exists and has a truthy value
        return JsonResponse(
            {"message": "You are not allowed to set a status during creation"},
            status=400,
        )

    # Retrieve user ID from session
    user_id = request.session.get("user_id")
    if not user_id:
        # Return 401 if user is not authenticated
        return JsonResponse({"message": "Authentication required."}, status=401)

    try:
        # Get the user object based on the ID
        current_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # Return 404 if the authenticated user doesn't exist in the DB
        return JsonResponse({"message": "User not found."}, status=404)

    # Initialize the serializer with request data
    # The 'user' field is NOT expected in the 'data' here
    serializer = ProposalSerializer(data=data)
    if not serializer.is_valid():
        # Return 400 with validation errors if data is invalid
        return JsonResponse(serializer.errors, status=400)

    # Save the serializer, passing the user object explicitly.
    # This correctly associates the proposal with the logged-in user.
    serializer.save(user=current_user)
    # Return 201 Created with the serialized new proposal data
    return JsonResponse(serializer.data, status=201)


@require_http_methods(["PUT"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "write")
def update_proposal(request, id):
    try:
        # Retrieve the proposal to update
        proposal = Proposal.objects.get(id=id)
    except Proposal.DoesNotExist:
        # Return 404 if the proposal doesn't exist
        return JsonResponse({"message": "Proposal not found."}, status=404)

    # Prevent updates if the proposal is already approved or rejected
    if proposal.status in ["approved", "rejected"]:  # Adjust status values if needed
        return JsonResponse(
            {
                "message": "You are not allowed to update a proposal with status approved or rejected"
            },
            status=400,
        )

    try:
        # Parse JSON data from the request body
        data = json.loads(request.body)
    except json.JSONDecodeError:
        # Return 400 if JSON is invalid
        return JsonResponse({"message": "Invalid JSON format"}, status=400)

    # Initialize the serializer with the existing proposal instance and new data
    # partial=True could be used here if you want to allow partial updates (PATCH)
    serializer = ProposalSerializer(proposal, data=data)
    if serializer.is_valid():
        # Save the updated proposal
        serializer.save()
        # Return 200 OK with the updated proposal data
        return JsonResponse(serializer.data, status=200)
    # Return 400 with validation errors if data is invalid
    return JsonResponse(serializer.errors, status=400)


@require_http_methods(["DELETE"])
@ensure_csrf_cookie
@check_user_permission([roles["admin"], roles["user"]], "proposal", "delete")
def delete_proposal(request, id):
    try:
        # Retrieve the proposal to delete
        proposal = Proposal.objects.get(id=id)
    except Proposal.DoesNotExist:
        # Return 404 if the proposal doesn't exist
        return JsonResponse({"message": "Proposal not found."}, status=404)
    # Delete the proposal instance
    proposal.delete()
    # Return 200 OK with a success message
    return JsonResponse({"message": "Proposal deleted successfully"}, status=200)

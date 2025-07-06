import os
import uuid
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .controller.amenity import (
    create_amenity,
    delete_amenity,
    get_amenity,
    list_amenities,
    update_amenity,
)
from .controller.booking_approvals import (
    approve_booking,
    get_approval_history,
    get_pending_approvals,
    reject_booking,
)
from .controller.club import (
    add_member_to_club,
    create_club,
    delete_club,
    get_all_clubs,
    get_all_clubs_details,
    get_all_members_of_club,
    get_club_by_id,
    get_my_clubs,
    remove_member_from_club,
    update_club,
)
from .controller.proposal import (
    create_proposal,
    delete_proposal,
    get_all_proposals,
    get_all_proposals_by_user,
    get_proposal_by_id,
    update_proposal,
)
from .controller.report import create_report
from .controller.venue import (
    create_venue,
    delete_venue,
    get_all_venues,
    get_venue_by_id,
    update_venue,
)
from .controller.venue_amenities import add_venue_amenity, list_venue_amenities
from .controller.venue_booking import (
    create_booking,
    get_all_bookings,
    get_booking_by_id,
    update_booking,
)
from .serializers import FileUploadSerializer
from .services.azure_blob_storage import AzureBlobStorage


class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data["file"]
            blob_storage = AzureBlobStorage()

            original_name = file.name
            name, ext = os.path.splitext(original_name)

            # Clean and format filename
            safe_name = "".join(
                c for c in name if c.isalnum() or c in ("_", "-")
            ).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_name = f"{safe_name}_{timestamp}_{uuid.uuid4().hex[:8]}{ext}"

            # Upload
            file_url = blob_storage.upload_file(unique_name, file.read())

            return Response({"file_url": file_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Venue API
def get_all_venues_view(request):
    return get_all_venues(request)


def get_venue_by_id_view(request, id):
    return get_venue_by_id(request, id)


def get_create_venue_view(request):
    return create_venue(request)


def get_update_venue_view(request, id):
    return update_venue(request, id)


def delete_venue_view(request, id):
    return delete_venue(request, id)


# Proposal API
def get_all_proposals_view(request):
    return get_all_proposals(request)


def get_all_proposals_by_user_view(request):
    return get_all_proposals_by_user(request)


def get_proposal_by_id_view(request, id):
    return get_proposal_by_id(request, id)


def create_proposal_view(request):
    return create_proposal(request)


def update_proposal_view(request, id):
    return update_proposal(request, id)


def delete_proposal_view(request, id):
    return delete_proposal(request, id)


# Venue Booking API
def create_venue_booking_view(request):
    return create_booking(request)


def get_all_bookings_view(request):
    return get_all_bookings(request)


def get_booking_by_id_view(request, id):
    return get_booking_by_id(request, id)


def update_booking_view(request, id):
    return update_booking(request, id)


# Booking Approvals API
def approve_booking_view(request, id):
    return approve_booking(request, id)


def reject_booking_view(request, id):
    return reject_booking(request, id)


def get_pending_approvals_view(request):
    return get_pending_approvals(request)


def get_approval_history_view(request, id):
    return get_approval_history(request, id)


# Club API
def create_club_view(request):
    return create_club(request)


def get_all_clubs_view(request):
    return get_all_clubs(request)


def get_all_club_details_view(request):
    return get_all_clubs_details(request)


def get_club_by_id_view(request, id):
    return get_club_by_id(request, id)


def update_club_view(request, id):
    return update_club(request, id)


def delete_club_view(request, id):
    return delete_club(request, id)


def add_member_to_club_view(request, id):
    return add_member_to_club(request, id)


def remove_member_from_club_view(request):
    return remove_member_from_club(request)


def get_all_members_of_club_view(request, id):
    return get_all_members_of_club(request, id)


def get_my_clubs_view(request):
    return get_my_clubs(request)


def create_amenity_view(request):
    return create_amenity(request)


def get_all_amenity_view(request):
    return list_amenities(request)


def get_amenity_by_id(request, id):
    return get_amenity(request, id)


def update_amenity_view(request, id):
    return update_amenity(request, id)


def delete_amenity_view(request, id):
    return delete_amenity(request, id)


def add_venue_amenity_view(request, venue_id):
    return add_venue_amenity(request, venue_id)


def get_amenities_of_a_venue_by_id_view(request, venue_id):
    return list_venue_amenities(request, venue_id)


def create_report_view(request):
    return create_report(request)

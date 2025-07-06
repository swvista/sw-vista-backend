# serializers.py
from rbac.models import User  # Import User model from rbac
from rest_framework import serializers

from .models.amenity import Amenity
from .models.booking import Booking

# Import models from their specific files
from .models.booking_approval import BookingApproval
from .models.club import Club
from .models.club_members import ClubMember
from .models.proposal import Proposal
from .models.Report import Report
from .models.venue import Venue
from .models.VenueAmenities import VenueAmenities


# Define UserSerializer for nested representation
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "name", "email"]


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = "__all__"


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = [
            "id",
            "name",
            "description",
            "requested_date",
            "duration_in_minutes",
            "attendees",
            "status",
            "created_at",
            "updated_at",
        ]


class BookingApprovalSerializer(serializers.ModelSerializer):
    approver_name = serializers.ReadOnlyField(source="approver.username")

    class Meta:
        model = BookingApproval
        fields = [
            "id",
            "booking",
            "approver",
            "approver_name",
            "stage",
            "status",
            "comments",
            "approval_date",
        ]
        read_only_fields = ["approval_date"]


class VenueBookingSerializer(serializers.ModelSerializer):
    # Existing fields
    approvals = BookingApprovalSerializer(many=True, read_only=True)
    venue_name = serializers.ReadOnlyField(source="venue.name")
    requester_name = serializers.ReadOnlyField(source="requester.username")
    status_display = serializers.ReadOnlyField(source="get_status_display")
    event_type_display = serializers.ReadOnlyField(source="get_event_type_display")

    # New nested representations (read-only)
    venue_details = VenueSerializer(source="venue", read_only=True)
    proposal_details = ProposalSerializer(
        source="proposal", read_only=True, allow_null=True
    )
    requester_details = UserSerializer(source="requester", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "venue",
            "venue_name",
            "venue_details",  # New field
            "proposal",
            "proposal_details",  # New field
            "event_type",
            "event_type_display",
            "requester",
            "requester_name",
            "requester_details",  # New field
            "approval_stage",
            "status",
            "status_display",
            "booking_date",
            "booking_duration",
            "created_at",
            "updated_at",
            "approvals",
        ]
        read_only_fields = ["approval_stage", "status", "created_at", "updated_at"]

    def validate(self, attrs):
        event_type = attrs.get("event_type")
        proposal = attrs.get("proposal")
        if event_type == 2 and proposal is None:
            raise serializers.ValidationError(
                {"proposal": "Proposal is required for event type 'event'."}
            )
        return attrs


class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = "__all__"


class ClubMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubMember
        fields = "__all__"


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"


class VenueAmenitiesSerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer(read_only=True)
    venue = VenueSerializer(read_only=True)

    class Meta:
        model = VenueAmenities
        fields = ["id", "venue", "amenity", "created_at", "updated_at"]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ["submitted_by", "submitted_at"]


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

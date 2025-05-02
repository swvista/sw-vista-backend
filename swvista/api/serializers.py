# serializers.py
from rest_framework import serializers

from .models.booking_approval import BookingApproval
from .models.proposal import Proposal
from .models.venue import Venue
from .models.venuebooking import VenueBooking


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
            "status",
            "created_at",
            "updated_at",
        ]


# class VenueBookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VenueBooking
#         fields = "__all__"

#     def validate(self, attrs):
#         event_type = attrs.get("event_type")
#         proposal = attrs.get("proposal")
#         if event_type == 2 and proposal is None:
#             raise serializers.ValidationError(
#                 {"proposal": "Proposal is required for event type 'event'."}
#             )
#         return attrs


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
    approvals = BookingApprovalSerializer(many=True, read_only=True)
    venue_name = serializers.ReadOnlyField(source="venue.name")
    requester_name = serializers.ReadOnlyField(
        source="requester.username"
    )  # Fixed source path
    status_display = serializers.ReadOnlyField(source="get_status_display")
    event_type_display = serializers.ReadOnlyField(source="get_event_type_display")

    class Meta:
        model = VenueBooking
        fields = [
            "id",
            "venue",
            "venue_name",
            "proposal",
            "event_type",
            "event_type_display",
            "requester",
            "requester_name",
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

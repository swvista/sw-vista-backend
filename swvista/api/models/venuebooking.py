from django.core.exceptions import ValidationError
from django.db import models

from .booking_approval import BookingApproval
from .proposal import Proposal
from .venue import Venue


class VenueBooking(models.Model):
    # Your existing fields...
    EVENT_TYPE = [
        (0, "practice"),
        (1, "general body meeting"),
        (2, "event"),
    ]
    # Status constants
    STATUS_PENDING = 0
    STATUS_APPROVED = 1
    STATUS_REJECTED = 2

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    requester = models.ForeignKey("rbac.User", on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    proposal = models.ForeignKey(
        Proposal, on_delete=models.CASCADE, null=True, blank=True
    )
    event_type = models.IntegerField(choices=EVENT_TYPE, default=0)
    # can be updated by the admin
    approval_stage = models.IntegerField(
        default=0,
    )  # Tracks current approval stage (0-3)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    booking_date = models.DateTimeField()
    booking_duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def approve(self, approver, comments=None):
        """Process an approval at the current stage"""
        if self.status == self.STATUS_REJECTED:
            return False

        # Create or update approval record
        approval, created = BookingApproval.objects.update_or_create(
            booking=self,
            stage=self.approval_stage,
            defaults={
                "approver": approver,
                "status": 1,  # Approved
                "comments": comments,
            },
        )

        # If this is the final approval (stage 3, becoming 4)
        if self.approval_stage == 3:
            self.status = self.STATUS_APPROVED
            self.save()
            return True

        # Move to next approval stage
        self.approval_stage += 1
        self.save()
        return True

    def reject(self, approver, comments=None):
        """Reject the booking at any stage"""
        if not comments:
            raise ValidationError("Comments are required when rejecting a booking")

        # Create or update approval record
        approval, created = BookingApproval.objects.update_or_create(
            booking=self,
            stage=self.approval_stage,
            defaults={
                "approver": approver,
                "status": 2,  # Rejected
                "comments": comments,
            },
        )

        self.status = self.STATUS_REJECTED
        self.save()
        return True

    def get_approval_history(self):
        """Get the full approval history"""
        return self.approvals.all()

    def clean(self):
        # Only require proposal if event_type == 2 ("event")
        if self.event_type == 2 and self.proposal is None:
            raise ValidationError(
                {"proposal": "Proposal is required for event type 'event'."}
            )

    def __str__(self):
        return f"{self.venue.name} - {self.proposal.name if self.proposal else 'No Proposal'}"

    class Meta:
        db_table = "venue_booking"

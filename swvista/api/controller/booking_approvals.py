import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from rbac.constants import roles
from rbac.decorators import session_login_required

from ..decorators import check_user_permission
from ..models.booking_approval import BookingApproval
from ..models.venuebooking import VenueBooking
from ..serializers import BookingApprovalSerializer, VenueBookingSerializer


@ensure_csrf_cookie
@session_login_required
@check_user_permission(roles["admin"], "venue", "approve")
def approve_booking(request, booking_id):
    """Approve a booking at the current stage"""
    if request.method == "POST":
        try:
            with transaction.atomic():
                booking = get_object_or_404(VenueBooking, id=booking_id)

                # Check if booking is already approved or rejected
                if booking.status != VenueBooking.STATUS_PENDING:
                    return JsonResponse(
                        {
                            "error": f"Booking is already {booking.get_status_display().lower()}."
                        },
                        status=400,
                    )

                # Get comments from request
                data = json.loads(request.body)
                comments = data.get("comments", "")

                # Create approval record for current stage
                approval, created = BookingApproval.objects.update_or_create(
                    booking=booking,
                    stage=booking.approval_stage,
                    defaults={
                        "approver_id": request.session.get("user_id"),
                        "status": BookingApproval.APPROVAL_STATUS[1][0],
                        "comments": comments,
                    },
                )

                # If this is the final approval stage (stage 3)
                if booking.approval_stage == 3:
                    booking.status = VenueBooking.STATUS_APPROVED
                    booking.save()
                    return JsonResponse(
                        {
                            "message": "Booking has been fully approved.",
                            "booking_id": booking.id,
                            "status": booking.get_status_display(),
                        }
                    )

                # Move to next approval stage
                booking.approval_stage += 1
                booking.save()

                return JsonResponse(
                    {
                        "message": f"Booking approved at stage {booking.approval_stage - 1}. Now at stage {booking.approval_stage}.",
                        "booking_id": booking.id,
                        "current_stage": booking.approval_stage,
                    }
                )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method is allowed."}, status=405)


@ensure_csrf_cookie
@session_login_required
@check_user_permission(roles["admin"], "venue", "reject")
def reject_booking(request, booking_id):
    """Reject a booking at any stage"""
    if request.method == "POST":
        try:
            with transaction.atomic():
                booking = get_object_or_404(VenueBooking, id=booking_id)

                # Check if booking is already approved or rejected
                if booking.status != VenueBooking.STATUS_PENDING:
                    return JsonResponse(
                        {
                            "error": f"Booking is already {booking.get_status_display().lower()}."
                        },
                        status=400,
                    )

                # Get comments from request
                data = json.loads(request.body)
                comments = data.get("comments")

                # Comments are required for rejection
                if not comments:
                    return JsonResponse(
                        {"error": "Comments are required when rejecting a booking."},
                        status=400,
                    )

                # Create rejection record
                approval, created = BookingApproval.objects.update_or_create(
                    booking=booking,
                    stage=booking.approval_stage,
                    defaults={
                        "approver_id": request.session.get("user_id"),
                        "status": BookingApproval.APPROVAL_STATUS[2][0],
                        "comments": comments,
                    },
                )

                # Update booking status
                booking.status = VenueBooking.STATUS_REJECTED
                booking.save()

                return JsonResponse(
                    {
                        "message": "Booking rejected.",
                        "booking_id": booking.id,
                        "status": booking.get_status_display(),
                        "rejection_stage": booking.approval_stage,
                        "rejection_comments": comments,
                    }
                )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method is allowed."}, status=405)


@ensure_csrf_cookie
@session_login_required
def get_pending_approvals(request):
    """Get list of bookings pending approval for the current user"""
    if request.method == "GET":
        try:

            pending_bookings = VenueBooking.objects.filter(
                status=VenueBooking.STATUS_PENDING
            )

            serializer = VenueBookingSerializer(pending_bookings, many=True)
            return JsonResponse(serializer.data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only GET method is allowed."}, status=405)


@ensure_csrf_cookie
@session_login_required
def get_approval_history(request, booking_id):
    """Get the full approval history for a booking"""
    if request.method == "GET":
        booking = get_object_or_404(VenueBooking, id=booking_id)
        approvals = booking.approvals.all()
        serializer = BookingApprovalSerializer(approvals, many=True)
        return JsonResponse(serializer.data, safe=False)
    return JsonResponse({"error": "Only GET method is allowed."}, status=405)

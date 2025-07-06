import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from rbac.decorators import check_user_permission, session_login_required

from ..models.booking import Booking
from ..serializers import VenueBookingSerializer


@ensure_csrf_cookie
@session_login_required
@check_user_permission([{"subject": "proposal", "action": "read"}])
def get_all_bookings(request):
    """Retrieve all venue bookings with detailed related data"""
    if request.method == "GET":
        # Optimized query with related data fetching
        bookings = (
            Booking.objects.select_related("venue", "proposal", "requester")
            .prefetch_related("approvals")
            .all()
        )

        serializer = VenueBookingSerializer(bookings, many=True)
        return JsonResponse(serializer.data, safe=False)
    return JsonResponse({"error": "Only GET method is allowed."}, status=405)


@ensure_csrf_cookie
@session_login_required
@check_user_permission([{"subject": "proposal", "action": "read"}])
def get_booking_by_id(request, booking_id):
    """Retrieve a specific booking by ID"""
    if request.method == "GET":
        booking = get_object_or_404(Booking, id=booking_id)
        serializer = VenueBookingSerializer(booking)
        return JsonResponse(serializer.data, safe=False)
    return JsonResponse({"error": "Only GET method is allowed."}, status=405)


@ensure_csrf_cookie
@session_login_required
@check_user_permission([{"subject": "proposal", "action": "read"}])
def create_booking(request):
    """Create a new venue booking"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Add requester from session
            data["requester"] = request.session.get("user_id")

            serializer = VenueBookingSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST method is allowed."}, status=405)


@ensure_csrf_cookie
@session_login_required
@check_user_permission([{"subject": "proposal", "action": "read"}])
def update_booking(request, booking_id):
    """Update an existing venue booking"""
    if request.method == "PUT":
        try:
            booking = get_object_or_404(Booking, id=booking_id)

            # Only allow updates if booking is still pending
            if booking.status != Booking.STATUS_PENDING:
                return JsonResponse(
                    {
                        "error": "Cannot update a booking that is already approved or rejected."
                    },
                    status=400,
                )

            data = json.loads(request.body)

            serializer = VenueBookingSerializer(booking, data=data)
            if serializer.is_valid():
                serializer.save()
                # Log the update (example)
                # logger.info(f"Booking {booking_id} updated by user {request.user.id}")
                return JsonResponse(serializer.data, status=200)
            else:
                # Log serializer errors for debugging
                # logger.error(f"Serializer errors: {serializer.errors}")
                return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Booking.DoesNotExist:  # Specific exception
            return JsonResponse({"error": "Booking not found."}, status=404)
        except Exception as e:
            # Log the exception
            # logger.exception("Unexpected error during booking update")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only PUT method is allowed."}, status=405)


@ensure_csrf_cookie
@session_login_required
@check_user_permission([{"subject": "proposal", "action": "read"}])
def delete_booking(request, booking_id):
    """Delete a venue booking"""
    if request.method == "DELETE":
        try:
            booking = get_object_or_404(Booking, id=booking_id)

            # Only allow deletion if booking is still pending
            if booking.status != Booking.STATUS_PENDING:
                return JsonResponse(
                    {
                        "error": "Cannot delete a booking that is already approved or rejected."
                    },
                    status=400,
                )

            booking.delete()
            return JsonResponse(
                {"message": "Booking deleted successfully."}, status=200
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only DELETE method is allowed."}, status=405)

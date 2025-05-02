from django.urls import path

from . import views

urlpatterns = [
    # Venue API
    path("venue/get-all/", views.get_all_venues_view, name="get_all_venues"),
    path(
        "venue/get-by-id/<int:id>/", views.get_venue_by_id_view, name="get_venue_by_id"
    ),
    path("venue/create/", views.get_create_venue_view, name="create_venue"),
    path("venue/update/<int:id>/", views.get_update_venue_view, name="update_venue"),
    path("venue/delete/<int:id>/", views.delete_venue_view, name="delete_venue"),
    # Proposal API
    path("proposal/get-all/", views.get_all_proposals_view, name="get_all_proposals"),
    path(
        "proposal/get-by-id/<int:id>/",
        views.get_proposal_by_id_view,
        name="get_proposal_by_id",
    ),
    path("proposal/create/", views.create_proposal_view, name="create_proposal"),
    path(
        "proposal/update/<int:id>/", views.update_proposal_view, name="update_proposal"
    ),
    path(
        "proposal/delete/<int:id>/", views.delete_proposal_view, name="delete_proposal"
    ),
    # Venue Booking API
    path(
        "booking/create/", views.create_venue_booking_view, name="create_venue_booking"
    ),
    path("booking/get-all/", views.get_all_bookings_view, name="get_all_bookings"),
    path(
        "booking/get-by-id/<int:id>/",
        views.get_booking_by_id_view,
        name="get_booking_by_id",
    ),
    path("booking/update/<int:id>/", views.update_booking_view, name="update_booking"),
    # Booking Approvals API
    path(
        "approvals/get-pending/",
        views.get_pending_approvals_view,
        name="get_pending_approvals",
    ),
    path(
        "approvals/approve/<int:id>/",
        views.approve_booking_view,
        name="approve_booking",
    ),
    path(
        "approvals/reject/<int:id>/", views.reject_booking_view, name="reject_booking"
    ),
]

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
    path(
        "proposal/get-all-by-user/",
        views.get_all_proposals_by_user_view,
        name="get_all_proposals_by_user",
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
    # Club API
    path("club/create/", views.create_club_view, name="create_club"),
    path("club/get-all/", views.get_all_clubs_view, name="get_all_clubs"),
    path(
        "club/get-all-club-details/",
        views.get_all_club_details_view,
        name="get_all_clubs_details",
    ),
    path("club/get-by-id/<int:id>/", views.get_club_by_id_view, name="get_club_by_id"),
    path("club/update/<int:id>/", views.update_club_view, name="update_club"),
    path("club/delete/<int:id>/", views.delete_club_view, name="delete_club"),
    path(
        "club/add-member/<int:id>/",
        views.add_member_to_club_view,
        name="add_member_to_club",
    ),
    path(
        "club/remove-member/",
        views.remove_member_from_club_view,
        name="remove_member_from_club",
    ),
    path(
        "club/get-all-members/<int:id>/",
        views.get_all_members_of_club_view,
        name="get_all_members_of_club",
    ),
    path("club/get-my-clubs/", views.get_my_clubs_view, name="get_my_clubs"),
    path("amenity/get-all/", views.get_all_amenity_view, name="get-all-amenity"),
    path("amenity/create/", views.create_amenity, name="create_amenity"),
    path(
        "amenity/get-by-id/<int:id>/", views.get_amenity_by_id, name="get_amenity_by_id"
    ),
    path(
        "amenity/update-by-id/<int:id>/",
        views.update_amenity_view,
        name="update_amenity",
    ),
    path(
        "amenity/delete-by-id/<int:id>/",
        views.delete_amenity_view,
        name="delete_amenity",
    ),
    path(
        "venueamenities/add/<int:venue_id>/",
        views.add_venue_amenity_view,
        name="add_venue_amenity",
    ),
    path(
        "venueamenities/get-by-id/<int:venue_id>/",
        views.get_amenities_of_a_venue_by_id_view,
        name="get_amenities_of_a_venue_by_id",
    ),
]

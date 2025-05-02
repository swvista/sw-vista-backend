from .controller.booking_approvals import (
    approve_booking,
    get_approval_history,
    get_pending_approvals,
    reject_booking,
)
from .controller.proposal import (
    create_proposal,
    delete_proposal,
    get_all_proposals,
    get_proposal_by_id,
    update_proposal,
)
from .controller.venue import (
    create_venue,
    delete_venue,
    get_all_venues,
    get_venue_by_id,
    update_venue,
)
from .controller.venue_booking import (
    create_booking,
    get_all_bookings,
    get_booking_by_id,
    update_booking,
)


# Venue API
def get_all_venues_view(request):
    return get_all_venues(request)


def get_venue_by_id_view(request):
    return get_venue_by_id(request)


def get_create_venue_view(request):
    return create_venue(request)


def get_update_venue_view(request, id):
    return update_venue(request, id)


def delete_venue_view(request, id):
    return delete_venue(request, id)


# Proposal API
def get_all_proposals_view(request):
    return get_all_proposals(request)


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

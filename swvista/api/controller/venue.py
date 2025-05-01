from api.models import Venue
from django.http import JsonResponse

# Controllers might be redundant, but they are useful for testing and development.


def get_venue_by_id(request, id):
    venue = Venue.objects.get_venue_by_id(id)
    return JsonResponse(venue)


def get_venue_by_name(request, name):
    venue = Venue.objects.get_venue_by_name(name)
    return JsonResponse(venue)


def get_venue_by_address(request, address):
    venue = Venue.objects.get_venue_by_address(address)
    return JsonResponse(venue)


def get_venue_by_latitude(request, latitude):
    venue = Venue.objects.get_venue_by_latitude(latitude)
    return JsonResponse(venue)


def get_venue_by_longitude(request, longitude):
    venue = Venue.objects.get_venue_by_longitude(longitude)
    return JsonResponse(venue)

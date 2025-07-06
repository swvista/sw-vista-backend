from django.contrib import admin

from .models import Venue
from .models.amenity import Amenity
from .models.booking import Booking
from .models.booking_approval import BookingApproval
from .models.booking_slot import BookingSlot
from .models.club import Club
from .models.club_members import ClubMember
from .models.event import Event
from .models.event_type import EventType
from .models.Report import Report
from .models.reschedule_booking import RescheduleLog
from .models.VenueAmenities import VenueAmenities

# Register your models here.


# Register all models
admin.site.register(Venue)
admin.site.register(Report)
admin.site.register(Amenity)
admin.site.register(VenueAmenities)
admin.site.register(BookingApproval)
admin.site.register(BookingSlot)
admin.site.register(Club)
admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(ClubMember)
admin.site.register(Booking)
admin.site.register(RescheduleLog)

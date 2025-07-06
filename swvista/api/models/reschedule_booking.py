from api.models.booking_slot import BookingSlot
from api.models.venue import Venue
from django.db import models
from rbac.models import User


class RescheduleLog(models.Model):
    slot = models.ForeignKey(BookingSlot, on_delete=models.CASCADE)
    previous_venue = models.ForeignKey(
        Venue, on_delete=models.SET_NULL, null=True, related_name="previous_slots"
    )
    new_venue = models.ForeignKey(
        Venue, on_delete=models.SET_NULL, null=True, related_name="rescheduled_slots"
    )
    previous_date = models.DateField()
    new_date = models.DateField()
    previous_start_time = models.TimeField()
    new_start_time = models.TimeField()
    previous_end_time = models.TimeField()
    new_end_time = models.TimeField()
    reason = models.TextField()
    rescheduled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reschedule_log"

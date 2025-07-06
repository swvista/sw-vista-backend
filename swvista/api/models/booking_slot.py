from api.models.booking import Booking
from api.models.venue import Venue
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class BookingSlot(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="slots")
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
        overlapping_slots = (
            BookingSlot.objects.filter(
                venue=self.venue,
                date=self.date,
            )
            .exclude(booking=self.booking)
            .filter(Q(start_time__lt=self.end_time) & Q(end_time__gt=self.start_time))
        )

        if overlapping_slots.exists():
            raise ValidationError(
                "This time slot conflicts with another booking for this venue."
            )

    class Meta:
        db_table = "booking_slot"
        unique_together = ("venue", "date", "start_time", "end_time")

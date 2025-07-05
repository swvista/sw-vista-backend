# api/models/venue_amenities.py
from api.models.amenity import Amenity
from api.models.venue import Venue
from django.db import models


class VenueAmenitiesManager(models.Manager):
    def add_amenity(self, venue_id, amenity_id):
        """Associate an amenity with a venue."""
        venue = Venue.objects.get(id=venue_id)  # Consider pre-checks as needed
        amenity = Amenity.objects.get(id=amenity_id)
        # Prevent duplicates
        obj, created = self.get_or_create(venue=venue, amenity=amenity)
        return obj

    def list_for_venue(self, venue_id):
        """Get all amenities for a specific venue."""
        return self.filter(venue_id=venue_id).select_related("amenity")

    def remove_amenity(self, venue_id, amenity_id):
        """Remove a specific amenity from a venue."""
        obj = self.get(venue_id=venue_id, amenity_id=amenity_id)
        obj.delete()
        return True

    def update_amenity(self, venue_id, old_amenity_id, new_amenity_id):
        """Change one amenity association to another for a venue."""
        obj = self.get(venue_id=venue_id, amenity_id=old_amenity_id)
        obj.amenity_id = new_amenity_id
        obj.save()
        return obj


class VenueAmenities(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    amenity = models.ForeignKey(
        Amenity, on_delete=models.CASCADE
    )  # Changed field name to lowercase!
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VenueAmenitiesManager()

    def __str__(self):
        return f"{self.venue.name} – {self.amenity.name}"

    class Meta:
        db_table = "venue_amenities"

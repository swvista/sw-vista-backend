from django.db import models


class VenueManager(models.Manager):
    def get_venue_by_id(self, id):
        return self.get(id=id)

    def get_venue_by_name(self, name):
        return self.get(name=name)

    def get_venue_by_address(self, address):
        return self.get(address=address)

    def get_venue_by_latitude(self, latitude):
        return self.get(latitude=latitude)

    def get_venue_by_longitude(self, longitude):
        return self.get(longitude=longitude)


class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to="venues/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VenueManager()

    def __str__(self):
        return self.name

from django.db import models


class AmenityManager(models.Manager):
    def create_amenity(self, name, description):
        return self.create(name=name, description=description)

    def list_amenities(self):
        return self.all()

    def get_amenity(self, id):
        return self.get(id=id)

    def update_amenity(self, id, **kwargs):
        amenity = self.get(id=id)
        for k, v in kwargs.items():
            setattr(amenity, k, v)
        amenity.save()
        return amenity

    def delete_amenity(self, id):
        amenity = self.get(id=id)
        amenity.delete()
        return True


class Amenity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AmenityManager()  # 🎯 Attach the custom manager

    def __str__(self):
        return self.name

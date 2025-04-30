# serializers.py
from rest_framework import serializers

from .models.venue import Venue


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = "__all__"

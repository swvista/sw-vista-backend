from django.db import models


class EventType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Practice, GBM, Event

    def __str__(self):
        return self.name

    class Meta:
        db_table = "event_type"

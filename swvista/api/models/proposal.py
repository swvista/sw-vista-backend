from django.db import models
from rbac.models import User


class Proposal(models.Model):
    PROPOSAL_STATUS = [
        (0, "pending"),
        (1, "approved"),
        (2, "rejected"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    requested_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    duration_in_minutes = models.IntegerField(default=0)
    attendees = models.IntegerField(default=0)
    status = models.IntegerField(choices=PROPOSAL_STATUS, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

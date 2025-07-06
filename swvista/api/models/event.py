from api.models.proposal import Proposal
from django.db import models
from rbac.models import User


class Event(models.Model):
    proposal = models.OneToOneField(
        Proposal, on_delete=models.PROTECT, related_name="proposal"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    creator_id = models.ForeignKey(User, on_delete=models.PROTECT, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "event"

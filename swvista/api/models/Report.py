from django.core.validators import FileExtensionValidator
from django.db import models
from rbac.models import User

from .club import Club
from .proposal import Proposal  # Import Proposal model


class Report(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    proposal = models.ForeignKey(
        Proposal, on_delete=models.CASCADE
    )  # Changed to ForeignKey
    title = models.CharField(max_length=200)
    participant_count = models.IntegerField()
    content = models.TextField()
    outcomes = models.TextField()
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)


class ReportAttachment(models.Model):
    report = models.ForeignKey(
        Report, related_name="attachments", on_delete=models.CASCADE
    )
    file = models.FileField(
        upload_to="reports/%Y/%m/%d/",
        validators=[FileExtensionValidator(["pdf", "docx", "jpg", "png"])],
    )

from django.db import models
from rbac.models import User

from .club import Club


class ClubMember(models.Model):
    # combination of club and user should be unique
    # using clubmember model to store the club and user relationship,
    # clould have used user model to store the club and user relationship but it would have been more complex
    # clubmember model is more flexible and can be used to store the club and user relationship in the future also its more readable
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("club", "user")

    def __str__(self):
        return f"{self.user.username} - {self.club.name}"

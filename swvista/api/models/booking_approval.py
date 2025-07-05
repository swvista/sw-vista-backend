from django.db import models


class BookingApproval(models.Model):
    APPROVAL_STATUS = [(0, "Pending"), (1, "Approved"), (2, "Rejected")]

    booking = models.ForeignKey(
        "api.venuebooking", on_delete=models.CASCADE, related_name="approvals"
    )
    approver = models.ForeignKey("rbac.User", on_delete=models.CASCADE)
    stage = models.IntegerField()
    status = models.IntegerField(choices=APPROVAL_STATUS, default=0)
    comments = models.TextField(blank=True, null=True)
    approval_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["booking", "stage"]
        ordering = ["stage"]
        db_table = "booking_approval"

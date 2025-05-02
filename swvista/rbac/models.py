from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.


class Permission(models.Model):
    """
    Permissions are the smallest unit of access control.
    They are grouped into P1 (Resource Type) and P2 (Action).
    """

    P1_CHOICES = (
        ("admin", "admin"),
        ("club", "club"),
        ("booking", "booking"),
        ("event", "event"),
        ("venue", "venue"),
        ("user", "user"),
        ("role", "role"),
        ("permission", "permission"),
        ("audit_log", "audit_log"),
    )
    P2_CHOICES = (
        ("read", "read"),
        ("write", "write"),
        ("delete", "delete"),
        ("update", "update"),
    )
    id = models.AutoField(primary_key=True)
    P1 = models.CharField(max_length=255, choices=P1_CHOICES, null=True, blank=True)
    P2 = models.CharField(max_length=255, choices=P2_CHOICES, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(Permission)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    registration_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_permission(self, permission_name):
        return self.role.permissions.filter(name=permission_name).exists()


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AuditLog(models.Model):
    """
    Records actions performed by users or the system for auditing purposes.
    """

    # --- Action Types ---
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_VIEW = "VIEW"  # Optional: If you need to log read access
    ACTION_MAP = "MAP"  # e.g., Map User to Role
    ACTION_UNMAP = "UNMAP"  # e.g., Unmap User Role
    # Add other relevant actions specific to your application

    ACTION_CHOICES = [
        (ACTION_CREATE, "Create"),
        (ACTION_UPDATE, "Update"),
        (ACTION_DELETE, "Delete"),
        (ACTION_LOGIN, "Login"),
        (ACTION_LOGOUT, "Logout"),
        (ACTION_VIEW, "View"),
        (ACTION_MAP, "Map"),
        (ACTION_UNMAP, "Unmap"),
        # ... add other choices here
    ]

    # --- Outcome Types ---
    OUTCOME_SUCCESS = "SUCCESS"
    OUTCOME_FAILURE = "FAILURE"

    OUTCOME_CHOICES = [
        (OUTCOME_SUCCESS, "Success"),
        (OUTCOME_FAILURE, "Failure"),
    ]

    # --- Fields ---

    # When the action occurred (auto_now_add handles 'When')
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp of when the action occurred.",
    )

    # Who performed the action ('Who' fields)
    actor = models.ForeignKey(
        # Use User model directly if it's your auth model, otherwise use settings.AUTH_USER_MODEL
        User,  # Assuming rbac.User is your AUTH_USER_MODEL for this project
        on_delete=models.SET_NULL,  # Keep log even if user is deleted
        null=True,
        blank=True,
        db_index=True,
        related_name="audit_logs",
    )
    remote_addr = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the client performing the action.",
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent string of the client ('Where'/Interface hint).",
    )

    # What action was performed ('What' fields)
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="The type of action performed.",
    )

    # Generic relation to the object being acted upon ('What' fields)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,  # Keep log even if ContentType changes/is removed (safer)
        null=True,
        blank=True,
        db_index=True,
        help_text="The model type of the object being acted upon (Resource Type).",
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="The primary key of the object being acted upon (Resource ID).",
    )
    content_object = GenericForeignKey("content_type", "object_id")

    # Store changes made ('Result' field)
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON representation of changes made (Old Value/New Value).",
    )

    # Result of the action ('Result' field)
    outcome = models.CharField(
        max_length=10,
        choices=OUTCOME_CHOICES,
        db_index=True,
        help_text="Outcome of the action (Success/Failure).",
    )

    # Additional Metadata
    description = models.TextField(
        blank=True,
        help_text="Optional human-readable description or notes about the event.",
    )

    class Meta:
        ordering = ("-timestamp",)  # Show newest logs first
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log Entries"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["actor"]),
            models.Index(fields=["action_type"]),
            models.Index(fields=["timestamp"]),
            # Add other indexes as needed based on common query patterns
        ]

    def __str__(self):
        actor_str = self.actor.username if self.actor else "System"
        target_str = (
            f"{self.content_type} ({self.object_id})"
            if self.content_type and self.object_id
            else "N/A"
        )
        return f"{self.timestamp}: [{self.outcome}] {actor_str} {self.get_action_type_display()} on {target_str}"

from app.models import TimeStampModelMixin
from django.db import models
import uuid

class Interaction(TimeStampModelMixin):
    CALL = "call"
    MESSAGE = "message"
    SPAM_REPORT = "spam_report"

    INTERACTION_TYPE_CHOICES = [
        (CALL, "Call"),
        (MESSAGE, "Message"),
        (SPAM_REPORT, "Spam Report"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiator = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="initiated_interactions"
    )
    receiver_user = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        related_name="received_interactions",
        null=True,
        blank=True
    )
    receiver_phone = models.CharField(max_length=15, blank=True, null=True, db_index=True)
    type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["initiator", "-timestamp"]),
            models.Index(fields=["receiver_phone"]),
            models.Index(fields=["type"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.initiator_id} -> {self.receiver_phone or self.receiver_user_id} ({self.type})"
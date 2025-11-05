from app.models import TimeStampModelMixin
from django.db import models
import uuid

class ScamRecord(TimeStampModelMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    reported_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='scam_records', null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='created_scam_records', null=True)
    updated_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='updated_scam_records', null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reported_by", "phone_number"],
                name="unique_phone_number_reported_by",
            ),
        ]

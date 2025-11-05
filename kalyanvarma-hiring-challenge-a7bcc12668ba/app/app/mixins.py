from django.db import models

class TimeStampModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        abstract = True
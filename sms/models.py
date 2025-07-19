from django.db import models
from django.utils import timezone

class SentSMS(models.Model):
    RECIPIENT_CHOICES = [
        ("guardian", "Guardian"),
        ("staff",    "Staff"),
        ("other",    "Other"),
    ]
    dest_addr      = models.CharField("Destination", max_length=13, db_index=True)
    first_name     = models.CharField(max_length=50, blank=True, null=True)
    last_name      = models.CharField(max_length=50, blank=True, null=True)
    message        = models.TextField()
    status         = models.CharField(max_length=16, default="Sent", db_index=True)
    sent_date      = models.DateTimeField(default=timezone.now, db_index=True)

    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_CHOICES,
                                      default="guardian")
    network        = models.CharField(max_length=50, blank=True, null=True)
    source_addr    = models.CharField(max_length=50, default="ST.TH-AVILA")
    length         = models.PositiveIntegerField(default=0)
    sms_count      = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-sent_date"]
        indexes  = [models.Index(fields=["dest_addr"]), models.Index(fields=["sent_date"])]

    def save(self, *args, **kwargs):
        if not self.length:
            self.length = len(self.message)
        if not self.sms_count:
            self.sms_count = ((len(self.message) - 1) // 160) + 1
        super().save(*args, **kwargs)
        
    def __str__(self) -> str:                      # noqa: D401
        name = f"{self.first_name or ''} {self.last_name or ''}".strip() or "N/A"
        return f"{name} – {self.dest_addr} ({self.status})"

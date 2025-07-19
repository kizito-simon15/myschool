from django.contrib import admin
from .models import SentSMS
@admin.register(SentSMS)
class SentSMSAdmin(admin.ModelAdmin):
    list_display = ("dest_addr", "sent_date", "status", "sms_count")
    list_filter  = ("status", "recipient_type", "source_addr")
    search_fields = ("dest_addr", "message")

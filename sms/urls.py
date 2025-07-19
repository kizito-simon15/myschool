from django.urls import path
from .views import SendSMSView, SMSHistoryView, CheckBalanceView, DeleteSMSView

urlpatterns = [
    path("send/",     SendSMSView.as_view(),     name="sms_send"),
    path("history/",  SMSHistoryView.as_view(),  name="sms_history"),
    path("balance/",  CheckBalanceView.as_view(),name="sms_balance"),
    path("delete/",   DeleteSMSView.as_view(),   name="delete_sms"),
]

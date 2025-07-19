from __future__ import annotations
from typing import List, Dict
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator


from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .utils import send_sms, _guardian_numbers, _staff_numbers 
from school.models import Student, Staff, SchoolClass, AcademicYear
from .beem_service import send_sms, check_balance
from .models import SentSMS

# ── helpers ────────────────────────────────────────────────────
def _tz(num: str) -> str:
    """Return +255XXXXXXXXX or '' if invalid."""
    if not num:
        return ""
    digits = "".join(filter(str.isdigit, num))
    if len(digits) == 12 and digits.startswith("255"):
        return "+" + digits
    if len(digits) == 9:
        return "+255" + digits
    return ""

def _guardian_numbers(stu: Student) -> List[Dict]:
    recs = []
    for num in (stu.guardian1_phone, stu.guardian2_phone):
        num = _tz(num)
        if num:
            recs.append({"dest_addr": num,
                         "first_name": stu.first_name,
                         "last_name":  stu.last_name})
    return recs

def _staff_numbers(qs) -> List[Dict]:
    uniq = {}
    for s in qs:
        num = _tz(s.phone)
        if num:
            uniq[num] = {"dest_addr": num,
                         "first_name": s.first_name,
                         "last_name":  s.last_name}
    return list(uniq.values())


# ── 1  Send form ───────────────────────────────────────────────
class SendSMSView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "sms.send_sms"
    template_name = "sms/send_sms.html"

    # ------------- GET -------------------------------------------------
    def get(self, request, *args, **kwargs):
        current_year = AcademicYear.objects.filter(is_current=True).first()

        context = {
            "students": Student.objects.filter(is_active=True)
                                       .prefetch_related("class_assignments__school_class"),
            "staff":    Staff.objects.filter(is_active=True),
            "classes":  (SchoolClass.objects.filter(academic_year=current_year)
                                            .order_by("name")
                        if current_year else SchoolClass.objects.none()),
        }
        # ALWAYS return a response
        return render(request, self.template_name, context)

    # ------------- POST ------------------------------------------------
    def post(self, request, *args, **kwargs):
        message = (request.POST.get("message") or "").strip()
        target  = request.POST.get("recipient_type")   # guardians | staff
        recipients: List[Dict] = []

        if target == "guardians":
            ids   = request.POST.getlist("student_ids")
            studs = Student.objects.filter(id__in=ids, is_active=True)
            for s in studs:
                recipients.extend(_guardian_numbers(s))

        elif target == "staff":
            ids = request.POST.getlist("staff_ids")
            recipients = _staff_numbers(
                Staff.objects.filter(id__in=ids, is_active=True)
            )

        # ---- validations ---------------------------------------------
        if not message:
            messages.error(request, "Message cannot be empty.")
            return redirect("sms_send")

        if not recipients:
            messages.error(request, "No valid recipients selected.")
            return redirect("sms_send")

        # dedupe by destination number
        recipients = list({r["dest_addr"]: r for r in recipients}.values())

        resp = send_sms(message, recipients)

        if resp.get("successful"):
            messages.success(request, f"SMS sent to {len(recipients)} recipient(s).")
        else:
            messages.error(
                request,
                f"Failed: {resp.get('error') or resp.get('message') or 'Unknown error'}",
            )
        return redirect("sms_send")

# ── 2  History ─────────────────────────────────────────────────
class SMSHistoryView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "sms.view_smshistory"
    template_name = "sms/sms_history.html"

    def get(self, request):
        qs = SentSMS.objects.all()
        ctx = {
            "messages":         qs[:500],
            "total":            qs.count(),
            "unique_numbers":   qs.values("dest_addr").distinct().count(),
        }
        return render(request, self.template_name, ctx)

# ── 3  Balance ────────────────────────────────────────────────
class CheckBalanceView(LoginRequiredMixin, View):
    template_name = "sms/check_balance.html"
    def get(self, request):
        resp = check_balance()
        ctx  = {"error": resp.get("error")} if "error" in resp else resp.get("data", {})
        return render(request, self.template_name, ctx)



@method_decorator(require_POST, name="dispatch")
class DeleteSMSView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "sms.delete_sentsms"

    def post(self, request):
        ids = request.POST.getlist("sms_ids")
        deleted = 0
        if ids:
            deleted, _ = SentSMS.objects.filter(id__in=ids).delete()
        # Ajax response so the JS can decide what to do next
        return JsonResponse({"deleted": deleted})
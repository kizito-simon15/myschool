# sms/utils.py  ───────────────────────────────────────────────
from typing import List, Dict
from school.models import Student, Staff

# ---- 1. Build guardian phone list --------------------------
def _guardian_numbers(student: Student) -> List[Dict]:
    out: List[Dict] = []
    if student.guardian1_phone:
        out.append({
            "dest_addr": student.guardian1_phone,
            "first_name": student.first_name,
            "last_name": student.last_name,
        })
    if student.guardian2_phone:
        out.append({
            "dest_addr": student.guardian2_phone,
            "first_name": student.first_name,
            "last_name": student.last_name,
        })
    return out

# ---- 2. Build staff phone list -----------------------------
def _staff_numbers(staff_qs) -> List[Dict]:
    return [
        {
            "dest_addr": s.phone,
            "first_name": s.first_name,
            "last_name": s.last_name,
        }
        for s in staff_qs if s.phone
    ]

# ---- 3. Actual SMS send ------------------------------------
def send_sms(message: str, recipients: List[Dict]) -> Dict:
    """
    Call your gateway here.
    Return a dict like {"successful": True} or {"successful": False, "error":"…"}
    """
    # 🔧  Replace the stub below with real gateway logic
    print("=== SMS OUT ===")
    print("Msg :", message)
    print("To  :", [r["dest_addr"] for r in recipients])
    print("===============")
    return {"successful": True}

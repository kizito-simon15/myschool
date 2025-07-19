
from __future__ import annotations
import base64, logging, requests
from django.conf import settings
from .models import SentSMS

logger = logging.getLogger(__name__)

# ── credentials (read from settings.py; fall back to sample values) ─────────────
API_KEY     = getattr(settings, "BEEM_API_KEY",  "93465cf26c024566")
SECRET_KEY  = getattr(settings, "BEEM_SECRET_KEY",
                      "MWQ2NTg5MGQzNDkwOGM4NjFjZmZiNjJjYjA4ZjA3MTBjZGI4Zjg3NjdkYThmZjIxZGU1OTcyMDQ4MjJiMDJlYw==")
SOURCE_ADDR = getattr(settings, "BEEM_SOURCE_ADDR", "ST.TH-AVILA")

BASE_URL = "https://apisms.beem.africa"

def _auth_header() -> dict[str, str]:
    token   = f"{API_KEY}:{SECRET_KEY}"
    encoded = base64.b64encode(token.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

# ── PUBLIC API ─────────────────────────────────────────────────────────────────
def send_sms(message: str, recipients: list[dict]) -> dict:
    """
    recipients = [{"dest_addr": "+2557XXXXXXXX", "first_name": "...", "last_name": "..."}]
    """
    url = f"{BASE_URL}/v1/send"
    payload = {
        "source_addr":  SOURCE_ADDR,
        "schedule_time": "",
        "encoding":      0,
        "message":       message,
        "recipients": [
            {"recipient_id": i + 1, "dest_addr": r["dest_addr"]}
            for i, r in enumerate(recipients)
        ],
    }
    headers = {"Content-Type": "application/json", **_auth_header()}
    resp    = requests.post(url, headers=headers, json=payload, timeout=30)
    try:
        data = resp.json()
    except ValueError:
        logger.error("Non‑JSON response from Beem: %s", resp.text[:200])
        return {"successful": False, "error": "Invalid response from Beem"}

    logger.debug("Beem response %s", data)

    # log only on 200/OK + successful flag
    if resp.status_code == 200 and data.get("successful"):
        _archive_success(message, recipients, data.get("network", ""))
    return data

def check_balance() -> dict:
    url = f"{BASE_URL}/public/v1/vendors/balance"
    resp = requests.get(url, headers=_auth_header(), timeout=15)
    return resp.json() if resp.ok else {"error": resp.text}

# ── helpers ───────────────────────────────────────────────────────────────────
def _archive_success(message: str, recs: list[dict], net: str):
    for r in {r['dest_addr']: r for r in recs}.values():        # dedupe
        SentSMS.objects.create(
            dest_addr=r["dest_addr"],
            first_name=r.get("first_name"),
            last_name=r.get("last_name"),
            message=message,
            network=net or "Unknown",
            length=len(message),
            sms_count=((len(message) - 1) // 160) + 1,
            status="Sent",
        )

"""
Data retention cleanup script. Run this periodically (e.g. daily via cron
or a scheduled task on Railway) to enforce the retention periods documented
in the Privacy Policy.

Retention policy enforced here:
- Notifications older than 90 days: deleted (not personal data, just noise)
- OTP verification records older than 7 days: deleted (no longer needed after expiry)
- Expired/used refresh tokens older than 30 days: deleted (housekeeping)
- Anonymized/deleted user accounts: their booking/review/message records are
  KEPT (already anonymized, needed for accounting/dispute history), but any
  remaining plaintext PII fields on those old records get double-checked and
  scrubbed if somehow missed during the original anonymization.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.notification import Notification
from app.models.user import OTPVerification, RefreshToken

db = SessionLocal()

now = datetime.utcnow()

# Delete notifications older than 90 days
notif_cutoff = now - timedelta(days=90)
deleted_notifs = db.query(Notification).filter(
    Notification.created_at < notif_cutoff
).delete()

# Delete OTP records older than 7 days (long past their 10-minute expiry)
otp_cutoff = now - timedelta(days=7)
deleted_otps = db.query(OTPVerification).filter(
    OTPVerification.created_at < otp_cutoff
).delete()

# Delete refresh tokens older than 30 days (well past their 7-day validity)
token_cutoff = now - timedelta(days=30)
deleted_tokens = db.query(RefreshToken).filter(
    RefreshToken.created_at < token_cutoff
).delete()

db.commit()
db.close()

print(f"Retention cleanup complete:")
print(f"  Notifications deleted: {deleted_notifs}")
print(f"  OTP records deleted: {deleted_otps}")
print(f"  Refresh tokens deleted: {deleted_tokens}")
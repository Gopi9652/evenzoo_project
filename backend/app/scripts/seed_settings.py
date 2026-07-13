import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.notification import PlatformSetting

db = SessionLocal()

settings_data = [
    {"key": "commission_rate", "value": "0.06", "description": "Platform commission percentage"},
    {"key": "min_booking_amount", "value": "1000", "description": "Minimum booking amount in INR"},
    {"key": "max_advance_days", "value": "365", "description": "Max days in advance a booking can be made"},
]

for s in settings_data:
    exists = db.query(PlatformSetting).filter(
        PlatformSetting.key == s["key"]
    ).first()
    if not exists:
        db.add(PlatformSetting(**s))

db.commit()
db.close()
print("✅ Settings seeded")
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.booking import EventType

db = SessionLocal()

event_types = [
    {"name": "Wedding"},
    {"name": "Engagement"},
    {"name": "Reception"},
    {"name": "Birthday Party"},
    {"name": "Anniversary"},
    {"name": "Baby Shower"},
    {"name": "Naming Ceremony"},
    {"name": "Housewarming"},
    {"name": "Half Saree Ceremony"},
    {"name": "Puberty Function"},
    {"name": "Mehendi"},
    {"name": "Haldi"},
    {"name": "Sangeet"},
    {"name": "Satyanarayana Vratam"},
    {"name": "Corporate Event"},
    {"name": "Conference"},
    {"name": "Seminar"},
    {"name": "Workshop"},
    {"name": "College Fest"},
    {"name": "School Function"},
    {"name": "Cultural Event"},
    {"name": "Religious Event"},
    {"name": "Farewell Party"},
    {"name": "Freshers Party"},
    {"name": "Product Launch"},
    {"name": "Charity Event"},
    {"name": "Other"}
]

for event in event_types:
    exists = db.query(EventType).filter(
        EventType.name == event["name"]
    ).first()

    if not exists:
        db.add(EventType(**event))

db.commit()
db.close()

print("✅ Event types seeded successfully")
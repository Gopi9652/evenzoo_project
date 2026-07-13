import sys
import os
#sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, BASE_DIR)


from app.database import SessionLocal
from app.models.vendor import VendorCategory

db = SessionLocal()

categories = [
    {"name": "Photography",    "icon": "📸"},
    {"name": "Catering",       "icon": "🍽️"},
    {"name": "Decoration",     "icon": "🌸"},
    {"name": "Music & DJ",     "icon": "🎵"},
    {"name": "Cakes & Sweets", "icon": "🎂"},
    {"name": "Transport",      "icon": "🚗"},
    {"name": "Makeup & Hair",  "icon": "💄"},
    {"name": "Videography",    "icon": "🎥"},
    {"name": "Venues",         "icon": "🏛️"},
    {"name": "Entertainment",  "icon": "🎪"},
]

for cat in categories:
    exists = db.query(VendorCategory).filter(
        VendorCategory.name == cat["name"]
    ).first()
    if not exists:
        db.add(VendorCategory(**cat))

db.commit()
db.close()
print("✅ Categories seeded")
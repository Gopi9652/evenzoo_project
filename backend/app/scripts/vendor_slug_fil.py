import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.vendor import VendorProfile
from app.utils.slug import generate_unique_slug

db = SessionLocal()
vendors = db.query(VendorProfile).filter(VendorProfile.slug.is_(None)).all()

for vendor in vendors:
    vendor.slug = generate_unique_slug(db, vendor.business_name)

db.commit()
db.close()
print(f"✅ Backfilled slugs for {len(vendors)} vendors")
import sys
import os
import random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.models.vendor import VendorProfile, VendorService, VendorCategoryMap, VendorCategory
from app.models.customer import CustomerProfile
from app.models.location import City
from app.utils.security import hash_password

db = SessionLocal()

FIRST_NAMES = ["Ravi", "Priya", "Arjun", "Sneha", "Vikram", "Anita", "Suresh", "Divya",
               "Karthik", "Meera", "Rajesh", "Pooja", "Sanjay", "Kavya", "Manoj"]
BUSINESS_TYPES = ["Photography", "Catering", "Decoration", "Music", "Cakes",
                   "Transport", "Makeup", "Videography", "Venues", "Entertainment"]

cities = db.query(City).all()
categories = db.query(VendorCategory).all()

if not cities or not categories:
    print("❌ Run seed_cities.py and seed_categories.py first!")
    sys.exit(1)

print("Creating 50 vendors...")
for i in range(1, 51):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(BUSINESS_TYPES)}"
    email = f"vendor{i}@loadtest.com"
    phone = f"90000{i:05d}"

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        continue

    user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=hash_password("Test@1234"),
        role="vendor",
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.flush()

    vendor = VendorProfile(
        user_id=user.id,
        business_name=f"{name} Services",
        description=f"Professional {random.choice(BUSINESS_TYPES).lower()} services with years of experience.",
        city_id=random.choice(cities).id,
        address=f"{random.randint(1,999)} Main Street",
        is_approved=(i <= 40),  # 40 approved, 10 pending — realistic mix
        avg_rating=round(random.uniform(3.5, 5.0), 2) if i <= 40 else 0,
        total_reviews=random.randint(0, 50) if i <= 40 else 0,
        total_bookings=random.randint(0, 30) if i <= 40 else 0
    )
    db.add(vendor)
    db.flush()

    # Add 2-4 services per vendor
    for _ in range(random.randint(2, 4)):
        db.add(VendorService(
            vendor_id=vendor.id,
            name=f"{random.choice(BUSINESS_TYPES)} Package",
            description="Full service package",
            price=random.randint(5000, 50000),
            price_type=random.choice(["fixed", "per_hour", "per_day", "per_person"]),
            is_active=True
        ))

    # Assign 1-2 categories
    for cat in random.sample(categories, k=min(2, len(categories))):
        db.add(VendorCategoryMap(vendor_id=vendor.id, category_id=cat.id))

db.commit()
print("✅ 50 vendors created")

print("Creating 100 customers...")
for i in range(1, 101):
    email = f"customer{i}@loadtest.com"
    phone = f"80000{i:05d}"

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        continue

    user = User(
        name=f"{random.choice(FIRST_NAMES)} Customer{i}",
        email=email,
        phone=phone,
        password_hash=hash_password("Test@1234"),
        role="customer",
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.flush()

    db.add(CustomerProfile(
        user_id=user.id,
        city_id=random.choice(cities).id,
        address=f"{random.randint(1,999)} Customer Lane"
    ))

db.commit()
db.close()
print("✅ 100 customers created")
print("\n📋 All test accounts use password: Test@1234")
print("Vendors: vendor1@loadtest.com to vendor50@loadtest.com")
print("Customers: customer1@loadtest.com to customer100@loadtest.com")
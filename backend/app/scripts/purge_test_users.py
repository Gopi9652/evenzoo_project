import sys, os, secrets
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password

db = SessionLocal()
users = db.query(User).filter((User.email.like("%@loadtest.com")) | (User.email.like("%@test.com"))).all()
for u in users:
    u.is_active = False
    u.password_hash = hash_password(secrets.token_urlsafe(32))
db.commit()
print(f"Disabled {len(users)} test accounts")
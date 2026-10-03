import re
import secrets


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def generate_unique_slug(db, business_name: str, vendor_id: int = None) -> str:
    """
    Builds a slug from the business name, appending a short random suffix
    to guarantee uniqueness without leaking sequential IDs (e.g. not
    'vendor-1', 'vendor-2' — those would just reintroduce the same
    enumeration problem in a different form).
    """
    from app.models.vendor import VendorProfile

    base = slugify(business_name) or "vendor"
    suffix = secrets.token_hex(3)  # 6 random hex chars
    candidate = f"{base}-{suffix}"

    # Extremely unlikely to collide, but check anyway
    while db.query(VendorProfile).filter(VendorProfile.slug == candidate).first():
        suffix = secrets.token_hex(3)
        candidate = f"{base}-{suffix}"

    return candidate
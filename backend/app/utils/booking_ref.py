import random
import string
from datetime import datetime

def generate_booking_ref() -> str:
    year = datetime.utcnow().year
    rand = ''.join(random.choices(string.digits, k=4))
    return f"EVZ-{year}-{rand}"
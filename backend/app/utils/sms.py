import requests
from app.config import settings


def send_otp_sms(phone: str, otp_code: str) -> bool:
    """
    Send OTP via MSG91. Returns True if sent successfully.
    Falls back to console print if MSG91 isn't configured yet.
    """
    if settings.MSG91_AUTH_KEY == "placeholder":
        print(f"[DEV MODE] OTP for {phone}: {otp_code}")
        return True

    url = "https://control.msg91.com/api/v5/otp"
    payload = {
        "template_id": settings.MSG91_TEMPLATE_ID,
        "mobile": f"91{phone}",
        "authkey": settings.MSG91_AUTH_KEY,
        "otp": otp_code
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"SMS sending failed: {e}")
        # Fallback — still print so you're not locked out during testing
        print(f"[FALLBACK] OTP for {phone}: {otp_code}")
        return False
import logging, threading, requests
from app.config import settings

logger = logging.getLogger("evenzoo.email")


def _send(to: str, subject: str, html: str, dev_link: str | None):
    if settings.ENVIRONMENT != "production" and "placeholder" in settings.RESEND_API_KEY:
        print(f"[DEV MODE] email to {to}: {subject} -> {dev_link}")   # dev only
        return
    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json={"from": settings.EMAIL_FROM, "to": [to], "subject": subject, "html": html},
            timeout=10,
        )
        r.raise_for_status()
    except requests.RequestException:
        logger.exception("Email send failed")          # never log the link or token


def send_email(to, subject, html, dev_link=None):
    # background thread: response time must not reveal whether the account exists
    threading.Thread(target=_send, args=(to, subject, html, dev_link), daemon=True).start()


def send_password_reset(to, token):
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    send_email(to, "Reset your Evenzoo password",
               f'<p>Click to reset your password (valid 1 hour):</p><p><a href="{link}">{link}</a></p>', link)


def send_email_change_confirmation(to, token):
    link = f"{settings.FRONTEND_URL}/settings/confirm-email?token={token}"
    send_email(to, "Confirm your new Evenzoo email",
               f'<p>Confirm your new email (valid 1 hour):</p><p><a href="{link}">{link}</a></p>', link)
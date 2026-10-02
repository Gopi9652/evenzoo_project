import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import settings

import asyncio

def send_email_sync(to_email: str, subject: str, html_body: str) -> bool:
    """Bridges the async send_email() into a sync caller, same pattern as websocket push_sync."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(send_email(to_email, subject, html_body))
            return True
        else:
            return loop.run_until_complete(send_email(to_email, subject, html_body))
    except RuntimeError:
        return asyncio.run(send_email(to_email, subject, html_body))
async def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Sends an email via SMTP. Falls back to console logging in dev mode
    when SMTP credentials aren't configured yet, mirroring the same
    dev-fallback pattern used for SMS OTP earlier in the build.
    """
    if settings.SMTP_USERNAME == "placeholder":
        print(f"[DEV MODE] Email to {to_email} | Subject: {subject}")
        print(f"[DEV MODE] Body: {html_body}")
        return True

    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        print(f"[FALLBACK] Email to {to_email} | Subject: {subject}")
        return False


def otp_email_template(otp_code: str, purpose: str) -> str:
    purpose_label = {
        "register": "verify your account",
        "login": "log in",
        "reset_password": "reset your password",
        "phone_change": "confirm your new phone number",
    }.get(purpose, "verify this request")

    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 24px;">
        <h2 style="color: #1A1A2E;">Evenzoo Verification Code</h2>
        <p style="color: #475569; font-size: 15px;">Use this code to {purpose_label}:</p>
        <div style="background: #FAF4EC; border-radius: 10px; padding: 20px; text-align: center; margin: 20px 0;">
            <span style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #E8650A;">{otp_code}</span>
        </div>
        <p style="color: #94A3B8; font-size: 13px;">This code expires in 10 minutes. If you didn't request this, you can safely ignore this email.</p>
    </div>
    """
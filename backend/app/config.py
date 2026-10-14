from pydantic_settings import BaseSettings
from pydantic import model_validator

class Settings(BaseSettings):
    DATABASE_URL: str
    TESTING: bool = False
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    JWT_SECRET: str = "KsfzhMyBzdGuVtpUMo-tYIH3tQ98xBYia5XccBrq4CbEEU5o15ZFuaujxKZCtysK"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    RAZORPAY_KEY_ID: str = "rzp_test_placeholder"
    RAZORPAY_KEY_SECRET: str = "placeholder"
    CLOUDINARY_URL: str = "cloudinary://placeholder"
    PLATFORM_COMMISSION: float = 0.06
    MSG91_AUTH_KEY:str="547333AaV9JizXzm6a489dd5P1"
    MSG91_TEMPLATE_ID:str="6a48a07008727cd0a50d9c22"
    CLOUDINARY_CLOUD_NAME: str = "elm5helo"
    CLOUDINARY_API_KEY: str = "916785571475724"
    CLOUDINARY_API_SECRET: str = "NihIvJC0ko43X0r2SRHqIDRAXDg"
    MESSAGE_ENCRYPTION_KEY: str = "tExog41sk102t-cbRQjk8its7M7V6mebksBSC8wcXnM="
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "placeholder"
    SMTP_PASSWORD: str = "placeholder"
    SMTP_FROM_EMAIL: str = "noreply@evenzoo.in"
    SMTP_FROM_NAME: str = "Evenzoo"
    OTP_CHANNEL: str = "email"   # "email" | "sms" | "both"
    ENVIRONMENT: str = "production"   # set to "production" in Render's env vars
    TRUSTED_PROXY_COUNT: int = 3
    REDIS_URL: str | None = None
    FIELD_ENCRYPTION_KEY: str | None = None
    RESEND_API_KEY: str | None = None
    CORS_ORIGINS: str = (
        "http://localhost:4200,"
        "http://127.0.0.1:4200"
    )
    @model_validator(mode="after")
    def refuse_unsafe_production(self):
        if self.ENVIRONMENT != "production":
            return self
        bad = []
        if len(self.JWT_SECRET) < 32 or "change" in self.JWT_SECRET.lower() or "placeholder" in self.JWT_SECRET.lower():
            bad.append("JWT_SECRET must be a random string of 32+ chars")
        for name in ("MESSAGE_ENCRYPTION_KEY", "FIELD_ENCRYPTION_KEY", "MSG91_AUTH_KEY", "MSG91_TEMPLATE_ID", "RESEND_API_KEY"):
            if "placeholder" in str(getattr(self, name, "placeholder")).lower():
                bad.append(f"{name} is still a placeholder")
        if "*" in self.CORS_ORIGINS:
            bad.append("CORS_ORIGINS must not contain *")
        if bad:
            raise ValueError("Unsafe production config: " + "; ".join(bad))
        return self
    class Config:
        env_file = ".env"

settings = Settings()
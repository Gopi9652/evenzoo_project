from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
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
    class Config:
        env_file = ".env"

settings = Settings()
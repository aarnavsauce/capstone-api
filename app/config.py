import os

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Capstone E-Commerce API")
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Security Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-capstone-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 60

    # webhook shared secret
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "my_super_secret_webhook_key_123")

settings = Settings()
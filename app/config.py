import os

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Capstone E-Commerce API")
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
from os import environ
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL: str = environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dimatech",
    )
    SECRET_KEY: str = environ.get("SECRET_KEY", "super-secret-key-change-in-production")
    JWT_SECRET: str = environ.get("JWT_SECRET", "jwt-secret-change-in-production")
    WEBHOOK_SECRET: str = environ.get("WEBHOOK_SECRET", "111111111111111111111111111111")
    DEBUG: bool = environ.get("DEBUG", "false").lower() == "true"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

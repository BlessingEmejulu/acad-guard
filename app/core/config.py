"""
Application Configuration settings loaded from environment or defaults.
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AcadGuard - Academic Project Management & Plagiarism Detection System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "acadguard-super-secret-production-key-2026-secure-plagiarism")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./academic_integrity.db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc", ".txt"]
    CORS_ORIGINS: List[str] = ["*"]
    
    # Plagiarism thresholds
    SIMILARITY_LOW_MAX: float = 19.99
    SIMILARITY_MODERATE_MAX: float = 39.99
    SIMILARITY_HIGH_MAX: float = 59.99

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

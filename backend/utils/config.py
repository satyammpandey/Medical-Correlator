"""
Configuration settings loaded from .env file
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Groq AI
    GROQ_API_KEY: str = "your_groq_api_key_here"
    GROQ_MODEL: str = "llama3-70b-8192"

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/medical_ai_db"

    # Security
    SECRET_KEY: str = "your_secret_key_here_minimum_32_chars"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Encryption
    ENCRYPTION_KEY: str = "your_32_byte_encryption_key_here!!"

    # Upload settings
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"

    # Chroma vector DB
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

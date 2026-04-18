# backend/core/config.py
# ============================================
# CONFIGURATION (Updated for DB and AI)
# ============================================

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Configuration for Medical AI Correlator.
    Loads values from .env file.
    """

    # App
    APP_NAME: str = "Medical AI Correlator"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # Database (PostgreSQL)
    # This is the line that was missing!
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/medical_db"

    # Redis (For caching/tasks)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Neo4j (Knowledge Graph)
    NEO4J_URI: str = "neo4j://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Pinecone (Vector DB)
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "medical-reports"

    # Groq API
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"   # Prevent crash from extra variables

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


# Create single instance used throughout the app
settings = Settings()
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from core.config import settings

# Create Async Engine (Converts postgresql:// to postgresql+asyncpg://)
DB_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    patient_id = Column(String, unique=True, index=True)
    gender = Column(String, default="Other")
    date_of_birth = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

async def get_db():
    async with SessionLocal() as session:
        yield session
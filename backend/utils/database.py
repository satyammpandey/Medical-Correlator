"""
Database setup using SQLAlchemy ORM
PostgreSQL for patient data storage
"""

from sqlalchemy import create_engine, Column, String, DateTime, JSON, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from utils.config import settings

# ─────────────────────────────────────────────
# DATABASE ENGINE
# ─────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using them
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─────────────────────────────────────────────
# DATABASE MODELS (Tables)
# ─────────────────────────────────────────────

class Patient(Base):
    """Stores patient information"""
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    date_of_birth = Column(String(20))
    gender = Column(String(20))
    patient_id = Column(String(50), unique=True)  # Hospital patient ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reports = relationship("MedicalReport", back_populates="patient")
    analyses = relationship("AnalysisResult", back_populates="patient")


class MedicalReport(Base):
    """Stores individual medical reports uploaded by patients"""
    __tablename__ = "medical_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    
    # File info
    filename = Column(String(500))
    file_path = Column(String(1000))
    file_type = Column(String(50))  # pdf, jpg, png, etc.
    
    # Report metadata (filled by Agent 1)
    report_type = Column(String(100))  # blood_test, xray, prescription, doctor_note
    report_date = Column(String(50))   # Date on the report
    report_title = Column(String(500))
    
    # Extracted content (filled by Agent 2 or 3)
    extracted_text = Column(Text)
    extracted_values = Column(JSON)  # e.g., {"glucose": 110, "hba1c": 6.2}
    abnormal_flags = Column(JSON)    # e.g., ["glucose_borderline", "hba1c_elevated"]
    
    # Processing status
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="reports")


class AnalysisResult(Base):
    """Stores the final AI analysis results for a patient"""
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"))
    
    # Correlation findings (Agent 4 output)
    correlations = Column(JSON)
    
    # Risk predictions (Agent 5 output)
    risk_scores = Column(JSON)      # e.g., {"diabetes": 89.3, "hypertension": 45.2}
    risk_level = Column(String(20)) # low, moderate, high, critical
    
    # Patient report (Agent 6 output)
    patient_summary = Column(Text)
    
    # Doctor recommendations (Agent 7 output)
    recommendations = Column(JSON)
    
    # Analysis metadata
    reports_analyzed = Column(JSON)  # List of report IDs included
    analysis_date = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)

    # Relationships
    patient = relationship("Patient", back_populates="analyses")


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def init_db():
    """Create all tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")


def get_db():
    """
    Dependency function for FastAPI routes.
    Provides a database session and ensures it's closed after use.
    
    Usage in routes:
        async def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

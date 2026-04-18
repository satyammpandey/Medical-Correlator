# backend/models/schemas.py
# ============================================
# DATA SCHEMAS
# Defines the structure of all data in the system
# Pydantic validates data types automatically
# ============================================

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS (Fixed value lists)
# ============================================

class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Severity(str, Enum):
    NORMAL = "NORMAL"
    BORDERLINE = "BORDERLINE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

class TrafficLight(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


# ============================================
# AGENT 1: CLASSIFICATION
# ============================================

class ClassificationResult(BaseModel):
    """Output from Agent 1 (Document Classifier)"""
    report_type: str
    confidence: float = 0
    report_date: str = "unknown"
    patient_name: str = "unknown"
    patient_age: Optional[str] = None
    patient_gender: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    key_findings_preview: List[str] = []
    is_abnormal: bool = False
    reasoning: str = ""
    error: Optional[str] = None


# ============================================
# AGENT 2: LAB ANALYSIS
# ============================================

class LabValue(BaseModel):
    """A single lab test value"""
    test_name: str
    test_category: str = "General"
    value: float
    unit: str = ""
    normal_min: Optional[float] = None
    normal_max: Optional[float] = None
    status: str = "NORMAL"  # NORMAL, HIGH, LOW, CRITICAL_HIGH, CRITICAL_LOW, BORDERLINE
    severity_score: int = 1  # 1-10
    significance: str = ""


class LabAnalysisResult(BaseModel):
    """Output from Agent 2 (Lab Report Analyzer)"""
    report_date: str
    values: List[LabValue] = []
    overall_severity: str = "NORMAL"
    abnormal_values: List[LabValue] = []
    summary: str = ""
    raw_text_length: int = 0
    error: Optional[str] = None


# ============================================
# AGENT 3: IMAGING ANALYSIS
# ============================================

class ImagingAnalysisResult(BaseModel):
    """Output from Agent 3 (Imaging Report Analyzer)"""
    report_date: str
    imaging_type: str  # xray, mri, ct, ultrasound
    key_findings: List[str] = []
    abnormalities: List[str] = []
    impression: str = ""
    severity: str = "NORMAL"
    requires_followup: bool = False
    urgency: str = "routine"


# ============================================
# AGENT 4: CORRELATION
# ============================================

class TrendAnalysis(BaseModel):
    """Trend analysis for a single test over time"""
    test_name: str
    data_points: int
    first_date: str
    last_date: str
    first_value: float
    last_value: float
    change_percent: float
    trend_direction: str  # INCREASING, DECREASING, STABLE
    is_concerning: bool = False
    unit: str = ""
    all_values: List = []  # List of (date, value) tuples


class Pattern(BaseModel):
    """A disease pattern found across multiple reports"""
    disease_name: str
    icd10_code: str = ""
    confidence_percentage: float
    risk_level: str
    evidence: List[Dict] = []
    cross_report_connections: List[str] = []
    reasoning: str = ""
    urgency: str = ""


class CorrelationResult(BaseModel):
    """Output from Agent 4 (Cross-Report Correlator)"""
    patient_id: str
    reports_analyzed: int
    time_span_days: int
    patterns_found: List[Pattern] = []
    trends: List[TrendAnalysis] = []
    cross_connections: List[Dict] = []
    summary: str = ""
    analysis_timestamp: str = ""


# ============================================
# AGENT 5: RISK PREDICTION
# ============================================

class DiseaseRisk(BaseModel):
    """Risk assessment for a single disease"""
    disease_name: str
    icd10_code: str = ""
    risk_percentage: float  # 0-100
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    confidence: float = 0
    five_year_risk: float = 0
    evidence_count: int = 0
    key_factors: List[str] = []
    protective_factors: List[str] = []
    immediate_actions: List[str] = []
    reasoning: str = ""
    urgency: str = ""
    source: str = ""  # rule_based or ai_enhanced


class RiskPredictionResult(BaseModel):
    """Output from Agent 5 (Risk Predictor)"""
    patient_age: Optional[int] = None
    patient_gender: str = "unknown"
    disease_risks: List[DiseaseRisk] = []
    overall_risk_level: str = "LOW"
    overall_risk_score: float = 0
    primary_concern: str = "None"
    analysis_basis: str = ""


# ============================================
# AGENT 6: PATIENT REPORT
# ============================================

class PatientReport(BaseModel):
    """Output from Agent 6 (Patient Report Generator)"""
    patient_name: str
    report_date: str
    headline: str
    what_we_found: str
    what_this_means: str
    what_to_do_next: str
    good_news: str = ""
    health_score: int = 50  # 0-100
    traffic_light_status: str = "YELLOW"  # GREEN, YELLOW, RED
    action_items: List[Dict] = []
    reports_analyzed: int = 0


# ============================================
# AGENT 7: RECOMMENDATIONS
# ============================================

class Recommendation(BaseModel):
    """A single medical recommendation"""
    type: str  # specialist, test, lifestyle, monitoring
    title: str
    description: str
    urgency: str = "ROUTINE"
    timeline: str = ""
    reason: str = ""


class RecommendationResult(BaseModel):
    """Output from Agent 7 (Recommendation Agent)"""
    overall_priority: str
    specialist_referrals: List[Dict] = []
    additional_tests: List[Dict] = []
    lifestyle_changes: List[Dict] = []
    monitoring_schedule: List[Dict] = []
    disclaimer: str = ""


# ============================================
# ORCHESTRATOR (Master)
# ============================================

class ProcessingStatus(BaseModel):
    """Current status of a processing job"""
    job_id: str
    status: str
    progress: int = 0  # 0-100
    message: str = ""
    updated_at: str = ""


class OrchestratorInput(BaseModel):
    """Input to start processing"""
    patient_id: str
    patient_name: str = "Patient"
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    file_paths: List[str]
    existing_conditions: List[str] = []
    current_medications: List[str] = []


class OrchestratorResult(BaseModel):
    """Complete output from the orchestrator pipeline"""
    job_id: str
    patient_id: str
    status: str
    files_processed: int = 0
    reports_analyzed: int = 0

    # Agent outputs
    classifications: List[Dict] = []
    correlation: Optional[CorrelationResult] = None
    risk_prediction: Optional[RiskPredictionResult] = None
    patient_report: Optional[PatientReport] = None
    recommendations: Optional[RecommendationResult] = None

    # Summary
    overall_risk_level: str = "UNKNOWN"
    top_risk_disease: str = "None"
    patterns_found: int = 0

    processing_time_seconds: float = 0
    completed_at: str = ""
    error: Optional[str] = None


# ============================================
# API REQUEST/RESPONSE MODELS
# ============================================

class PatientCreateRequest(BaseModel):
    """Create a new patient"""
    name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    patient_id: Optional[str] = None  # External ID


class AnalysisStartResponse(BaseModel):
    """Response when analysis starts"""
    job_id: str
    patient_id: str
    status: str = "STARTED"
    message: str = "Analysis started. Poll /status/{job_id} for updates."
    estimated_time_minutes: int = 2


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

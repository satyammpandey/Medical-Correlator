"""
🤖 AGENT 1: Document Classifier & Parser
─────────────────────────────────────────
Identifies what type of medical report was uploaded.
Uses Groq LLM for classification with keyword fallback.
"""

from groq import Groq
import json
import re
# Updated this line to match your actual config location
from core.config import settings 

class DocumentClassifierAgent:
    """Classifies uploaded medical documents into categories."""

    REPORT_TYPES = [
        "blood_test", "imaging_report", "prescription", "doctor_note",
        "pathology", "eye_report", "kidney_report", "cardiac_report",
        "specialist_report", "unknown"
    ]

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def classify(self, text: str, filename: str = "") -> dict:
        """
        Classify a medical document based on its text content.
        Returns a dictionary with report_type, title, date, confidence etc.
        """
        text_sample = text[:3000] if len(text) > 3000 else text

        prompt = f"""You are a medical document classification expert.
Analyze this medical document and classify it.

FILENAME: {filename}
DOCUMENT TEXT:
{text_sample}

Respond ONLY with a valid JSON object:
{{
    "report_type": "<one of: blood_test, imaging_report, prescription, doctor_note, pathology, eye_report, kidney_report, cardiac_report, specialist_report, unknown>",
    "report_title": "<specific title like 'Complete Blood Count'>",
    "report_date": "<date in YYYY-MM-DD format or 'unknown'>",
    "doctor_name": "<doctor name or 'unknown'>",
    "hospital_lab": "<hospital or lab name or 'unknown'>",
    "confidence": <float 0.0-1.0>,
    "key_findings_preview": "<one line summary>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical AI. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
            )
            result_text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(result_text)

        except Exception as e:
            print(f"Agent 1 error: {e}")
            return self._fallback_classification(text, filename)

    def _fallback_classification(self, text: str, filename: str) -> dict:
        """Keyword-based fallback classification."""
        combined = (text + " " + filename).lower()

        if any(k in combined for k in ["blood", "glucose", "hemoglobin", "cbc", "lipid", "cholesterol", "hba1c"]):
            report_type = "blood_test"
        elif any(k in combined for k in ["x-ray", "xray", "mri", "ct scan", "ultrasound", "radiology"]):
            report_type = "imaging_report"
        elif any(k in combined for k in ["prescription", "medication", "tablet", "capsule"]):
            report_type = "prescription"
        elif any(k in combined for k in ["retina", "eye", "ophthalmology", "vision"]):
            report_type = "eye_report"
        elif any(k in combined for k in ["kidney", "renal", "creatinine", "microalbumin"]):
            report_type = "kidney_report"
        elif any(k in combined for k in ["biopsy", "pathology", "histology"]):
            report_type = "pathology"
        else:
            report_type = "doctor_note"

        return {
            "report_type": report_type,
            "report_title": f"Medical Report ({report_type.replace('_', ' ').title()})",
            "report_date": "unknown",
            "doctor_name": "unknown",
            "hospital_lab": "unknown",
            "confidence": 0.5,
            "key_findings_preview": "Classified using keyword matching"
        }

# ============================================================
# ADD THIS FUNCTION BELOW - This is what orchestrator.py needs
# ============================================================
def classify_document(state: dict) -> dict:
    """
    Orchestrator-compatible function.
    Expects state to have 'raw_text' and 'filename'.
    """
    agent = DocumentClassifierAgent()
    
    # Get text from the state (check if your state uses 'text' or 'raw_text')
    text = state.get("raw_text") or state.get("text", "")
    filename = state.get("filename", "document.pdf")
    
    # Run classification
    classification_results = agent.classify(text, filename)
    
    # Return updated state
    return {
        **state,
        "classification": classification_results
    }
"""
🤖 AGENT 3: Imaging Report Analyzer - FIXED VERSION
─────────────────────────────────────────────────────
FIXED: Was using OpenAI (crashed silently). Now uses Groq only.
Handles: X-ray, MRI, CT, Eye exam, ECG, Kidney reports
"""

import json
import re
from groq import Groq
from core.config import settings


class ImagingReportAnalyzerAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def analyze(self, text: str, report_type: str = "imaging_report", report_date: str = "unknown") -> dict:
        text_sample = text[:4000] if len(text) > 4000 else text

        prompt = f"""You are an expert radiologist and medical specialist AI.
Analyze this {report_type.replace('_', ' ')} report text carefully.

REPORT DATE: {report_date}
REPORT TEXT:
{text_sample}

Return ONLY valid JSON (no extra text before or after):
{{
    "modality": "<X-Ray / MRI / CT / Ultrasound / Eye Exam / ECG / Pathology / General>",
    "body_part": "<which body part was examined>",
    "key_findings": [
        {{
            "finding": "<description of what was found>",
            "severity": "<normal / mild / moderate / severe>",
            "clinical_significance": "<what this means medically>",
            "location": "<where in the body>"
        }}
    ],
    "abnormalities": ["<list of abnormal things found as simple strings>"],
    "impression": "<overall specialist impression in 1-2 sentences>",
    "abnormalities_detected": true,
    "follow_up_recommended": true,
    "follow_up_reason": "<why follow up is needed>",
    "disease_hints": ["<possible conditions this suggests, e.g. diabetic retinopathy, hypertension>"],
    "severity": "NORMAL",
    "severity_score": 5,
    "urgency": "routine"
}}

For severity_score: 1=completely normal, 5=moderate concern, 8=serious, 10=critical
For severity: NORMAL, MILD, MODERATE, SEVERE, or CRITICAL"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical imaging AI. Return valid JSON ONLY — no markdown, no explanation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500,
            )
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            match = re.search(r'\{.*\}', content, re.DOTALL)
            result = json.loads(match.group() if match else content)
            result.update({"report_date": report_date, "report_type": report_type})
            return result
        except Exception as e:
            print(f"Agent 3 error: {e}")
            return self._fallback(text, report_type, report_date)

    def _fallback(self, text: str, report_type: str, report_date: str) -> dict:
        """Keyword-based fallback when AI fails."""
        text_lower = text.lower()
        abnormals = []
        disease_hints = []

        keyword_map = [
            (["retinal", "retinopathy", "microaneurysm", "haemorrhage", "exudate"], "Diabetic retinopathy signs detected", "type2_diabetes"),
            (["microalbumin", "nephropathy", "proteinuria", "egfr reduced"], "Kidney damage indicators", "chronic_kidney_disease"),
            (["hypertension", "elevated bp", "blood pressure high", "140/90", "systolic 14"], "Hypertension signs", "cardiovascular_disease"),
            (["lv hypertrophy", "lvh", "cardiomegaly", "st change"], "Cardiac abnormality", "cardiovascular_disease"),
            (["opacity", "infiltrate", "consolidation", "effusion"], "Pulmonary finding", "respiratory"),
            (["nodule", "mass", "lesion", "suspicious"], "Suspicious finding requiring follow-up", "unknown"),
        ]

        for keywords, finding, hint in keyword_map:
            if any(k in text_lower for k in keywords):
                abnormals.append(finding)
                if hint not in disease_hints:
                    disease_hints.append(hint)

        return {
            "modality": report_type.replace("_", " ").title(),
            "body_part": "unspecified",
            "key_findings": [{"finding": a, "severity": "moderate", "clinical_significance": a, "location": "unspecified"} for a in abnormals],
            "abnormalities": abnormals,
            "impression": "; ".join(abnormals) if abnormals else "No major abnormalities detected from keyword scan.",
            "abnormalities_detected": len(abnormals) > 0,
            "follow_up_recommended": len(abnormals) > 0,
            "follow_up_reason": "Abnormalities detected" if abnormals else "Routine follow-up",
            "disease_hints": disease_hints,
            "severity": "MODERATE" if abnormals else "NORMAL",
            "severity_score": 5 if abnormals else 1,
            "urgency": "soon" if abnormals else "routine",
            "report_date": report_date,
            "report_type": report_type
        }


# Orchestrator wrapper
def analyze_imaging_report(state: dict) -> dict:
    agent = ImagingReportAnalyzerAgent()
    report_type = state.get("classification", {}).get("report_type", "imaging_report")
    report_date = state.get("classification", {}).get("report_date", "unknown")
    result = agent.analyze(state.get("raw_text", ""), report_type, report_date)
    return {**state, "imaging_analysis": result}

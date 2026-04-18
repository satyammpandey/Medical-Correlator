"""
🤖 AGENT 2: Lab Report Analyzer - FIXED VERSION
─────────────────────────────────────────────────
Extracts lab values with EXACT key names and proper abnormal detection.
"""

import json
import re
from groq import Groq
from core.config import settings

# ─── Normal ranges for flagging ───────────────────────────────────────────────
NORMAL_RANGES = {
    "glucose":            {"low": 70,   "high": 99,   "unit": "mg/dL",  "danger_high": 126},
    "fasting_glucose":    {"low": 70,   "high": 99,   "unit": "mg/dL",  "danger_high": 126},
    "hba1c":              {"low": 0,    "high": 5.6,  "unit": "%",      "danger_high": 6.5},
    "total_cholesterol":  {"low": 0,    "high": 199,  "unit": "mg/dL",  "danger_high": 240},
    "ldl":                {"low": 0,    "high": 99,   "unit": "mg/dL",  "danger_high": 160},
    "hdl":                {"low": 60,   "high": 999,  "unit": "mg/dL",  "invert": True},
    "triglycerides":      {"low": 0,    "high": 149,  "unit": "mg/dL",  "danger_high": 200},
    "creatinine":         {"low": 0.6,  "high": 1.2,  "unit": "mg/dL",  "danger_high": 1.5},
    "microalbumin":       {"low": 0,    "high": 30,   "unit": "mg/g",   "danger_high": 300},
    "hemoglobin":         {"low": 12.0, "high": 17.0, "unit": "g/dL"},
    "tsh":                {"low": 0.4,  "high": 4.0,  "unit": "mIU/L"},
    "uric_acid":          {"low": 2.5,  "high": 7.2,  "unit": "mg/dL"},
    "egfr":               {"low": 90,   "high": 999,  "unit": "mL/min", "invert": True},
    "systolic_bp":        {"low": 90,   "high": 120,  "unit": "mmHg",   "danger_high": 140},
    "diastolic_bp":       {"low": 60,   "high": 80,   "unit": "mmHg",   "danger_high": 90},
    "insulin":            {"low": 2.6,  "high": 24.9, "unit": "µIU/mL"},
    "bun":                {"low": 7,    "high": 25,   "unit": "mg/dL"},
    "post_prandial_glucose": {"low": 70, "high": 140, "unit": "mg/dL",  "danger_high": 200},
}


class LabReportAnalyzerAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def analyze(self, text: str) -> dict:
        """Extract lab values and flag abnormals."""
        ai_result = self._ai_extract(text)
        values = ai_result.get("values", {})

        # Also run regex extraction as backup and merge
        regex_values = self._regex_extract(text)
        for k, v in regex_values.items():
            if k not in values:
                values[k] = v

        # Generate abnormal flags from values
        abnormal_flags = self._flag_abnormals(values)

        return {
            "values": values,
            "abnormal_flags": abnormal_flags,
            "units": ai_result.get("units", {}),
            "clinical_notes": ai_result.get("clinical_notes", ""),
        }

    def _ai_extract(self, text: str) -> dict:
        text_sample = text[:4000] if len(text) > 4000 else text

        prompt = f"""You are a lab report extraction AI. Extract EVERY numerical test value from this report.

MEDICAL REPORT TEXT:
{text_sample}

YOU MUST return valid JSON with EXACTLY this structure:
{{
    "values": {{
        "glucose": 110,
        "hba1c": 6.1,
        "total_cholesterol": 198,
        "ldl": 128,
        "hdl": 42,
        "triglycerides": 168,
        "creatinine": 1.18,
        "hemoglobin": 14.2,
        "microalbumin": 48,
        "tsh": 2.4,
        "systolic_bp": 142,
        "diastolic_bp": 90,
        "egfr": 72,
        "bun": 22,
        "uric_acid": 7.2,
        "insulin": 15.8,
        "post_prandial_glucose": 198,
        "fasting_glucose": 126
    }},
    "units": {{
        "glucose": "mg/dL"
    }},
    "clinical_notes": "brief summary of key findings"
}}

RULES:
- Use lowercase_with_underscores for ALL keys
- Use only NUMERIC values (no strings like "Normal")
- Only include tests that ARE PRESENT in the text
- Map synonyms: "Fasting Blood Glucose" -> "fasting_glucose", "Hb" or "Haemoglobin" -> "hemoglobin", "LDL-C" -> "ldl", "HbA1c" -> "hba1c"
- If Systolic BP is 140/90, set systolic_bp=140, diastolic_bp=90
- Do NOT include tests with non-numeric results"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract lab values into JSON. Return ONLY the JSON object, no other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=1000,
            )
            content = response.choices[0].message.content.strip()
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(content)
        except Exception as e:
            print(f"Agent 2 AI error: {e}")
            return {"values": {}, "units": {}, "clinical_notes": ""}

    def _regex_extract(self, text: str) -> dict:
        """Regex fallback to extract common values."""
        patterns = {
            "fasting_glucose":   r"fasting\s+(?:blood\s+)?glucose[:\s]+(\d+\.?\d*)",
            "glucose":           r"\bglucose[:\s]+(\d+\.?\d*)",
            "hba1c":             r"hba1c[:\s]+(\d+\.?\d*)",
            "total_cholesterol": r"(?:total\s+)?cholesterol[:\s]+(\d+\.?\d*)",
            "ldl":               r"\bldl[:\s]+(\d+\.?\d*)",
            "hdl":               r"\bhdl[:\s]+(\d+\.?\d*)",
            "triglycerides":     r"triglycerides?[:\s]+(\d+\.?\d*)",
            "creatinine":        r"\bcreatinine[:\s]+(\d+\.?\d*)",
            "hemoglobin":        r"(?:haemoglobin|hemoglobin|hgb?|hb)[:\s]+(\d+\.?\d*)",
            "microalbumin":      r"microalbumin[:\s]+(\d+\.?\d*)",
            "egfr":              r"egfr[:\s]+(\d+\.?\d*)",
            "systolic_bp":       r"(?:bp|blood\s+pressure)[:\s]+(\d+)/",
            "diastolic_bp":      r"(?:bp|blood\s+pressure)[:\s]+\d+/(\d+)",
            "tsh":               r"\btsh[:\s]+(\d+\.?\d*)",
            "bun":               r"\bbun[:\s]+(\d+\.?\d*)",
        }
        found = {}
        text_lower = text.lower()
        for key, pattern in patterns.items():
            m = re.search(pattern, text_lower)
            if m:
                try:
                    found[key] = float(m.group(1))
                except:
                    pass
        return found

    def _flag_abnormals(self, values: dict) -> list:
        """Compare each value against normal ranges."""
        flags = []
        for test, value in values.items():
            if not isinstance(value, (int, float)):
                continue
            ranges = NORMAL_RANGES.get(test)
            if not ranges:
                continue

            invert = ranges.get("invert", False)  # For HDL/eGFR where low is bad

            if invert:
                # Low is bad
                if value < ranges["low"]:
                    flags.append({
                        "test": test,
                        "value": value,
                        "unit": ranges.get("unit", ""),
                        "status": "low",
                        "severity": "danger" if value < ranges["low"] * 0.8 else "warning",
                        "message": f"{test.replace('_',' ').title()} is LOW ({value} {ranges.get('unit','')})"
                    })
            else:
                danger_high = ranges.get("danger_high", ranges["high"] * 1.3)
                if value >= danger_high:
                    flags.append({
                        "test": test,
                        "value": value,
                        "unit": ranges.get("unit", ""),
                        "status": "critical_high",
                        "severity": "danger",
                        "message": f"{test.replace('_',' ').title()} is CRITICALLY HIGH ({value} {ranges.get('unit','')})"
                    })
                elif value > ranges["high"]:
                    flags.append({
                        "test": test,
                        "value": value,
                        "unit": ranges.get("unit", ""),
                        "status": "high",
                        "severity": "warning",
                        "message": f"{test.replace('_',' ').title()} is elevated ({value} {ranges.get('unit','')})"
                    })
                elif value < ranges["low"]:
                    flags.append({
                        "test": test,
                        "value": value,
                        "unit": ranges.get("unit", ""),
                        "status": "low",
                        "severity": "warning",
                        "message": f"{test.replace('_',' ').title()} is LOW ({value} {ranges.get('unit','')})"
                    })
        return flags


# Orchestrator wrapper
def analyze_lab_report(state: dict) -> dict:
    agent = LabReportAnalyzerAgent()
    result = agent.analyze(state.get("raw_text", ""))
    return {**state, "lab_analysis": result}

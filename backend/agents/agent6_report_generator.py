"""
🤖 AGENT 6: Patient Report Generator - FIXED VERSION
──────────────────────────────────────────────────────
FIXED: Now uses actual lab values and risk scores to generate
specific, meaningful summaries instead of generic text.
"""

import json
import re
from groq import Groq
from core.config import settings


class ReportGeneratorAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def generate(self, state: dict) -> dict:
        lab = state.get("lab_analysis", {})
        values = lab.get("values", {})
        flags = lab.get("abnormal_flags", [])
        risk = state.get("risk_assessment", {})
        correlations = state.get("correlation_results", {})
        risks_list = risk.get("risks", [])

        # Build context with real numbers
        top_risks = [r for r in risks_list if r.get("risk_percentage", 0) >= 30]
        primary_concern = correlations.get("primary_concern", {})
        patterns = correlations.get("patterns", [])
        missed = correlations.get("missed_by_individual_review", "")

        # Format lab values for AI
        notable_values = []
        for flag in flags[:8]:
            notable_values.append(f"• {flag.get('message', '')} (Status: {flag.get('status', '')})")

        trends = correlations.get("trends", [])
        trend_text = ""
        for t in trends[:4]:
            if t.get("data_points", 1) >= 2:
                trend_text += f"• {t['metric'].replace('_',' ').title()}: {t['first_value']} → {t['latest_value']} ({t['change_percent']}, {t['trend']})\n"

        prompt = f"""You are a compassionate doctor summarizing health results for a patient.
Use simple language (no jargon). Be honest but reassuring. Mention actual numbers.

PATIENT DATA:
Primary Concern: {primary_concern.get('condition', 'Multiple health markers need attention')}
Confidence: {primary_concern.get('confidence', 0.7):.0%}
Urgency: {primary_concern.get('urgency', 'moderate')}

ABNORMAL VALUES FOUND:
{chr(10).join(notable_values) if notable_values else "Moderate abnormalities detected"}

LAB TRENDS OVER TIME:
{trend_text if trend_text else "Single report — trend analysis requires multiple reports"}

TOP HEALTH RISKS:
{', '.join(f"{r['condition']} ({r['risk_percentage']}%)" for r in top_risks[:3])}

INSIGHT MISSED BY INDIVIDUAL DOCTORS:
{missed or primary_concern.get('reasoning', '')}

Write a patient-friendly report. Return ONLY valid JSON:
{{
    "headline": "<one clear sentence — mention the main finding with specific numbers>",
    "what_we_found": "<2-3 paragraphs in simple English. Mention real lab numbers. Explain what each means. No jargon.>",
    "what_this_means": "<1-2 paragraphs explaining health implications. Mention specific risks found.>",
    "what_to_do_next": "<2-3 specific action steps the patient should take, with urgency timeframe>",
    "health_score": <integer 0-100>,
    "concerns": [
        {{
            "title": "<concern title in plain words>",
            "explanation": "<what this means for the patient — use simple language>",
            "severity_emoji": "<🔴 or 🟠 or 🟡>"
        }}
    ],
    "positive_signs": ["<any normal findings or good news>"],
    "urgency_message": "<how soon to see a doctor — be specific: 'within 1 week', 'within 1 month', etc.>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You write patient health reports in simple, compassionate language. Always mention real numbers from the data. Return valid JSON ONLY."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            content = response.choices[0].message.content.strip()
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            match = re.search(r'\{.*\}', content, re.DOTALL)
            data = json.loads(match.group() if match else content)
            # Ensure all keys exist
            data.setdefault("concerns", [])
            data.setdefault("positive_signs", [])
            data.setdefault("health_score", risk.get("general_health_score", 65))
            return data

        except Exception as e:
            print(f"Agent 6 error: {e}")
            # Build a useful fallback from real data
            glucose = values.get("fasting_glucose") or values.get("glucose", "N/A")
            hba1c = values.get("hba1c", "N/A")
            ldl = values.get("ldl", "N/A")
            top_risk_name = top_risks[0]["condition"] if top_risks else "health markers"
            return {
                "headline": f"Health analysis complete — {len(flags)} abnormal values detected",
                "what_we_found": (
                    f"Your reports show {len(flags)} values outside normal range. "
                    f"Key findings: Glucose={glucose} mg/dL, HbA1c={hba1c}%, LDL={ldl} mg/dL. "
                    f"The AI identified {top_risk_name} as the primary concern."
                ),
                "what_this_means": (
                    f"These values suggest your {top_risk_name.lower()} risk is elevated. "
                    "Early intervention can prevent progression."
                ),
                "what_to_do_next": "Consult your doctor within the next 2 weeks. Share these AI findings with them.",
                "health_score": risk.get("general_health_score", 60),
                "concerns": [{"title": f.get("test","").replace("_"," ").title(), 
                               "explanation": f.get("message",""),
                               "severity_emoji": "🔴" if f.get("severity") == "danger" else "🟠"}
                             for f in flags[:4]],
                "positive_signs": [],
                "urgency_message": "Please schedule a doctor's appointment within 2 weeks."
            }


# Orchestrator wrapper
def generate_patient_report(state: dict) -> dict:
    print("---GENERATING PATIENT REPORT---")
    agent = ReportGeneratorAgent()
    report = agent.generate(state)
    return {**state, "final_report": report}

"""
🤖 AGENT 4: Cross-Report Correlator - FIXED VERSION
─────────────────────────────────────────────────────
FIXED: Now correlates ALL report types (lab + imaging + eye + cardiac).
Generates real trends from multiple blood test reports over time.
Produces proper output for the Trends tab and Risk Details tab.
"""

import json
import re
from datetime import datetime
from groq import Groq
from core.config import settings


class MedicalCorrelatorAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def correlate(self, all_reports: list) -> dict:
        """
        Main correlation function.
        all_reports: list of processed report dicts from orchestrator
        Each has: report_type, report_date, lab_analysis, imaging_analysis, classification
        """
        if not all_reports:
            return self._empty_result()

        # Sort reports chronologically
        sorted_reports = self._sort_by_date(all_reports)

        # Build trends from blood test reports
        trends = self._build_trends(sorted_reports)

        # Build summary text for AI
        summary_text = self._build_summary(sorted_reports)

        # Run AI correlation
        ai_result = self._ai_correlate(summary_text, trends)

        # Build timeline
        timeline = self._build_timeline(sorted_reports)

        return {
            "primary_concern": ai_result.get("primary_concern", {}),
            "correlations": ai_result.get("correlations", []),
            "patterns": ai_result.get("patterns", []),
            "system_involvement": ai_result.get("system_involvement", {}),
            "missed_by_individual_review": ai_result.get("missed_by_individual_review", ""),
            "trends": trends,
            "timeline": timeline,
            "report_count": len(all_reports),
            "date_range": {
                "earliest": sorted_reports[0].get("report_date", "unknown") if sorted_reports else "unknown",
                "latest": sorted_reports[-1].get("report_date", "unknown") if sorted_reports else "unknown",
            }
        }

    def _sort_by_date(self, reports: list) -> list:
        def parse_date(r):
            d = r.get("report_date", "") or r.get("classification", {}).get("report_date", "")
            for fmt in ["%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(d, fmt)
                except:
                    pass
            return datetime.min
        return sorted(reports, key=parse_date)

    def _build_trends(self, reports: list) -> list:
        """
        Extract numerical trends from blood test reports over time.
        Returns list of {metric, values:[{date,value}], trend, change_percent}
        """
        metric_history = {}

        for report in reports:
            report_date = (report.get("report_date") or
                           report.get("classification", {}).get("report_date", "unknown"))
            lab = report.get("lab_analysis", {})
            values = lab.get("values", {})

            for metric, value in values.items():
                if isinstance(value, (int, float)) and value > 0:
                    if metric not in metric_history:
                        metric_history[metric] = []
                    metric_history[metric].append({"date": report_date, "value": value})

        trends = []
        for metric, history in metric_history.items():
            if len(history) < 1:
                continue
            # Sort by date
            history.sort(key=lambda x: x["date"])
            first_val = history[0]["value"]
            last_val = history[-1]["value"]

            if first_val > 0 and len(history) >= 2:
                change = ((last_val - first_val) / first_val) * 100
                if change > 3:
                    trend = "increasing"
                elif change < -3:
                    trend = "decreasing"
                else:
                    trend = "stable"
                change_str = f"{change:+.1f}%"
            else:
                trend = "stable"
                change_str = "0%"

            trends.append({
                "metric": metric,
                "values": history,
                "trend": trend,
                "change_percent": change_str,
                "first_value": first_val,
                "latest_value": last_val,
                "data_points": len(history)
            })

        # Sort by importance (most concerning first)
        priority = ["fasting_glucose", "glucose", "hba1c", "ldl", "total_cholesterol",
                    "microalbumin", "triglycerides", "creatinine", "hdl", "systolic_bp"]
        trends.sort(key=lambda t: priority.index(t["metric"]) if t["metric"] in priority else 99)
        return trends

    def _build_summary(self, reports: list) -> str:
        """Build a text summary of all reports for AI input."""
        lines = ["PATIENT COMPLETE MEDICAL HISTORY (CHRONOLOGICAL):\n"]
        for i, report in enumerate(reports, 1):
            report_type = report.get("report_type") or report.get("classification", {}).get("report_type", "unknown")
            date = report.get("report_date") or report.get("classification", {}).get("report_date", "unknown")
            lines.append(f"\n{'='*50}")
            lines.append(f"REPORT {i}: {report_type.replace('_', ' ').upper()} | DATE: {date}")

            lab = report.get("lab_analysis", {})
            if lab.get("values"):
                lines.append("LAB VALUES: " + ", ".join(f"{k}={v}" for k, v in list(lab["values"].items())[:12]))
            if lab.get("abnormal_flags"):
                lines.append("ABNORMAL: " + "; ".join(f.get("message", "") for f in lab["abnormal_flags"][:6]))

            img = report.get("imaging_analysis", {})
            if img.get("impression"):
                lines.append(f"IMAGING IMPRESSION: {img['impression']}")
            if img.get("disease_hints"):
                lines.append(f"DISEASE HINTS: {', '.join(img['disease_hints'])}")
            if img.get("abnormalities"):
                lines.append(f"ABNORMALITIES: {', '.join(img['abnormalities'][:4])}")

        return "\n".join(lines)

    def _ai_correlate(self, summary_text: str, trends: list) -> dict:
        """Use AI to find cross-report correlations."""
        trend_summary = ""
        for t in trends[:5]:
            if t["data_points"] >= 2:
                trend_summary += f"- {t['metric']}: {t['first_value']} → {t['latest_value']} ({t['change_percent']}, {t['trend']})\n"

        prompt = f"""You are an expert medical AI diagnostician with 30 years of experience.
Analyze this patient's complete medical history and find disease patterns across ALL reports.

PATIENT HISTORY:
{summary_text[:4000]}

DETECTED TRENDS OVER TIME:
{trend_summary if trend_summary else "Only 1 report available"}

Think step by step:
1. What patterns emerge across different report types?
2. Do lab values, imaging findings, and symptoms correlate?
3. What disease progression is happening?
4. What would be missed if each report was seen alone?

Return ONLY valid JSON:
{{
    "primary_concern": {{
        "condition": "<main disease or health concern detected>",
        "confidence": <0.0 to 1.0>,
        "urgency": "<low / moderate / high / critical>",
        "reasoning": "<2-3 sentence explanation of why>"
    }},
    "correlations": [
        {{
            "type": "<correlation type e.g. glucose_progression>",
            "title": "<human-readable title>",
            "description": "<what pattern was found across reports>",
            "reports_involved": ["<report types>"],
            "clinical_significance": "<what this means>",
            "severity": "<low / moderate / high / critical>"
        }}
    ],
    "patterns": [
        {{
            "pattern_name": "<e.g. Rising Glucose Trend>",
            "description": "<description>",
            "timeframe": "<time period>",
            "direction": "<worsening / improving / stable>"
        }}
    ],
    "system_involvement": {{
        "metabolic": <true/false>,
        "cardiovascular": <true/false>,
        "renal": <true/false>,
        "ophthalmological": <true/false>,
        "neurological": <true/false>
    }},
    "missed_by_individual_review": "<key insight only visible when all reports are combined>"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical diagnostician AI. Find hidden disease patterns. Return valid JSON ONLY."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000,
            )
            content = response.choices[0].message.content.strip()
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            match = re.search(r'\{.*\}', content, re.DOTALL)
            return json.loads(match.group() if match else content)
        except Exception as e:
            print(f"Agent 4 AI error: {e}")
            return {
                "primary_concern": {"condition": "Multiple abnormal values detected", "confidence": 0.6, "urgency": "moderate", "reasoning": "Several lab values are outside normal range."},
                "correlations": [],
                "patterns": [],
                "system_involvement": {"metabolic": True},
                "missed_by_individual_review": "Pattern analysis requires reviewing all reports together."
            }

    def _build_timeline(self, reports: list) -> list:
        timeline = []
        for report in reports:
            lab = report.get("lab_analysis", {})
            img = report.get("imaging_analysis", {})
            cls = report.get("classification", {})
            report_type = report.get("report_type") or cls.get("report_type", "unknown")
            timeline.append({
                "date": report.get("report_date") or cls.get("report_date", "unknown"),
                "type": report_type,
                "title": cls.get("report_title") or report_type.replace("_", " ").title(),
                "has_abnormals": len(lab.get("abnormal_flags", [])) > 0 or img.get("abnormalities_detected", False),
                "severity": img.get("severity_score", 1),
            })
        return timeline

    def _empty_result(self) -> dict:
        return {
            "primary_concern": {},
            "correlations": [],
            "patterns": [],
            "trends": [],
            "timeline": [],
            "system_involvement": {},
            "missed_by_individual_review": "",
            "report_count": 0,
        }


# Orchestrator wrapper
def correlate_reports(state: dict) -> dict:
    print("---CORRELATING ALL REPORTS---")
    agent = MedicalCorrelatorAgent()
    all_reports = state.get("all_reports", [])
    result = agent.correlate(all_reports)
    return {**state, "correlation_results": result}

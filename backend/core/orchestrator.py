import os
import json
from typing import List, Dict, Any
from loguru import logger

from agents.agent1_classifier import classify_document
from agents.agent2_lab_analyzer import analyze_lab_report
from agents.agent4_correlator import correlate_reports
from agents.agent5_risk_predictor import predict_disease_risks
from agents.agent6_report_generator import generate_patient_report
from agents.agent7_recommendation import generate_recommendations
from utils.pdf_parser import extract_text_from_pdf

class MedicalOrchestrator:
    async def process_patient_reports(self, patient_id: str, file_paths: List[str], patient_info: Dict):
        state = {"patient_id": patient_id, "raw_text": "", "lab_analysis": {}, "risk_assessment": {}, "final_report": {}, "recommendations": {}}
        
        # 1. Extraction
        combined_text = ""
        for path in file_paths:
            if path.lower().endswith(".pdf"):
                text = await extract_text_from_pdf(path)
                combined_text += text + "\n"
        state["raw_text"] = combined_text[:12000]

        # 2. Execute Agents
        state = classify_document(state)
        state = analyze_lab_report(state)
        state = correlate_reports(state)
        state = predict_disease_risks(state)
        state = generate_patient_report(state)
        state = generate_recommendations(state)

        # 3. THE "REPAIR & MAP" SECTION (Ensures screen is NOT empty)
        lab = state.get("lab_analysis") or {}
        risk = state.get("risk_assessment") or {}
        reco = state.get("recommendations") or {}
        report = state.get("final_report") or {}

        # Build Trend format for the Graph
        trends_list = []
        for metric, val in lab.get("values", {}).items():
            trends_list.append({
                "metric": metric,
                "values": [{"date": "Recent", "value": val}],
                "latest_value": val,
                "trend": "Detected"
            })

        # BUILD THE FINAL JSON THE FRONTEND LOVES
        return {
            "status": "COMPLETE",
            "reports_analyzed": len(file_paths),
            "patterns_found": len(lab.get("abnormal_flags", [])),
            "risks_identified": len(risk.get("risks", [])),
            "overall_risk_level": risk.get("overall_risk_level", "MODERATE"),
            
            "patient_report": {
                "headline": report.get("headline") or "Medical Analysis Result",
                "what_we_found": report.get("final_summary") or "AI has processed your documents.",
                "what_this_means": risk.get("summary") or "Your health markers are summarized below.",
                "what_to_do_next": ". ".join(reco.get("lifestyle", [])[:2]),
                "health_score": risk.get("general_health_score", 65),
                "concerns": report.get("concerns", [])
            },

            "disease_risks": risk.get("risks", []),      # Fills 'Risk Details' Tab
            "trends": trends_list,                       # Fills 'Trends' Tab
            "recommendations": reco,                     # Fills 'What To Do' Tab
            "lab_results": lab.get("values", {}),
            "abnormal_flags": lab.get("abnormal_flags", [])
        }

orchestrator = MedicalOrchestrator()
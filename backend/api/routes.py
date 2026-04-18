# backend/api/routes.py
import os
import uuid
import aiofiles
from pathlib import Path
from typing import List, Optional, Dict
from loguru import logger
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks, Body
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db, Patient
from core.config import settings
from core.orchestrator import orchestrator

# Initialize routers
patients = APIRouter()
reports = APIRouter()
analysis = APIRouter()

# In-memory job storage
active_jobs = {}

# ============================================
# 1. PATIENTS ROUTER
# ============================================

@patients.post("/patients")
async def create_patient(data: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """Handles frontend call: POST /api/v1/patients"""
    try:
        new_p = Patient(
            name=data.get("name"),
            gender=data.get("gender", "Other"),
            date_of_birth=data.get("date_of_birth"),
            patient_id=str(uuid.uuid4())[:8].upper()
        )
        db.add(new_p)
        await db.commit()
        await db.refresh(new_p)
        logger.success(f"✅ Created Patient: {new_p.name}")
        return {"id": str(new_p.id), "patient_id": new_p.patient_id, "status": "success"}
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Patient Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# 2. REPORTS ROUTER (UPLOAD)
# ============================================

@reports.post("/patients/{patient_id}/upload-reports")
async def upload_reports(patient_id: str, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """Handles frontend call: POST /api/v1/patients/{id}/upload-reports"""
    try:
        logger.info(f"📥 Received {len(files)} files for Patient {patient_id}")
        
        # Save files
        upload_dir = Path(settings.UPLOAD_DIR) / str(patient_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []
        
        for file in files:
            file_path = upload_dir / f"{uuid.uuid4()}{Path(file.filename).suffix}"
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(await file.read())
            saved_paths.append(str(file_path))

        # Create job tracking
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        active_jobs[job_id] = {"status": "RUNNING", "progress": 10}

        # Start Background AI
        background_tasks.add_task(run_ai_pipeline, job_id, patient_id, saved_paths)
        
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        logger.error(f"❌ Upload Failed: {e}")
        raise HTTPException(status_code=500, detail="Internal file error")

# ============================================
# 3. ANALYSIS ROUTER (STATUS & RESULTS)
# ============================================

@analysis.get("/status/{job_id}")
async def check_status(job_id: str):
    """Handles frontend polling: GET /api/v1/status/{id}"""
    # Check if job exists
    job = active_jobs.get(job_id)
    if not job:
        return {"status": "NOT_FOUND", "progress": 0}
    
    # If the AI is done, the 'result' key will be in the dictionary
    return job

# ============================================
# BACKGROUND WORKER (PREVENTS EMPTY SECTIONS)
# ============================================

async def run_ai_pipeline(job_id: str, patient_id: str, file_paths: List[str]):
    try:
        logger.info(f"🤖 AI Pipeline Starting: {job_id}")
        
        # This calls your 7 agents
        result = await orchestrator.process_patient_reports(
            patient_id=patient_id, 
            file_paths=file_paths, 
            patient_info={}
        )

        # Store the full result including trends/risks/recommendations
        active_jobs[job_id] = {
            "status": "COMPLETE",
            "progress": 100,
            "result": result
        }
        logger.success(f"✅ AI Job {job_id} Finished Successfully")
        
    except Exception as e:
        logger.error(f"❌ AI Pipeline Crash: {e}")
        active_jobs[job_id] = {"status": "FAILED", "error": str(e)}
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from loguru import logger

from core.config import settings
from api.routes import patients, reports, analysis # Unified import

app = FastAPI(title="Medical AI Correlator", version="1.0.0")

# CORS: Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# --- MOUNT ROUTERS ---
# Base prefix is /api/v1. The paths inside routes.py will complete the URL.
app.include_router(patients, prefix="/api/v1", tags=["Patients"])
app.include_router(reports, prefix="/api/v1", tags=["Reports"])
app.include_router(analysis, prefix="/api/v1", tags=["AI Analysis"])

# Startup: Verify Database
@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting Medical AI System...")
    try:
        from core.database import engine, Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.success("✅ Database tables verified")
    except Exception as e:
        logger.error(f"❌ Database setup issue: {e}")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"status": "🏥 Medical AI System is Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
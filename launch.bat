@echo off
title Medical AI - Force Fix Launcher
color 0A
cd /d "%~dp0"

echo [1/4] Killing old processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo [2/4] Ensuring Databases are running (Port 5433)...
cd docker
docker compose up -d
cd ..

echo [3/4] FORCING BACKEND INSTALL...
cd backend
if not exist "venv\" ( python -m venv venv )
call venv\Scripts\activate

:: This line forces the installation of the packages you are missing
echo      Installing critical PDF libraries...
python -m pip install --upgrade pip
pip install pdfplumber pdf2image pytesseract asyncpg groq langchain loguru

echo      Starting Backend Server...
start "BACKEND" cmd /k "venv\Scripts\activate && uvicorn main:app --reload --port 8000"
cd ..

echo [4/4] Starting Frontend...
start "FRONTEND" cmd /k "cd frontend && npm run dev"

echo =======================================================
echo ✅ DATABASE, BACKEND, AND FRONTEND ARE STARTING
echo =======================================================
timeout /t 5
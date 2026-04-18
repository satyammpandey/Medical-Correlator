# 🏥 Agentic AI Medical Report Correlator & Early Disease Risk Predictor

A patent-grade AI system that analyzes multiple medical reports over time to detect disease risks early.

---

## 📋 TABLE OF CONTENTS
1. [What This System Does](#what-it-does)
2. [Software You Need to Install](#software-required)
3. [Project Structure](#project-structure)
4. [Setup Instructions (Step by Step)](#setup)
5. [How to Run](#running)
6. [API Keys Required](#api-keys)

---

## 🎯 What This System Does

- Patient uploads blood tests, X-rays, prescriptions, doctor notes
- 7 AI Agents analyze ALL reports together
- System finds hidden patterns across time
- Generates risk alerts (e.g., "89% chance of Type 2 Diabetes progression")
- Produces patient-friendly summary + doctor recommendations

---

## 💻 Software Required

### Install These First (in order):

| Software | Version | Download Link | Why Needed |
|----------|---------|---------------|------------|
| Python | 3.11+ | https://python.org | Backend language |
| Node.js | 18+ | https://nodejs.org | Frontend |
| Git | Latest | https://git-scm.com | Code management |
| Docker | Latest | https://docker.com | Database containers |
| VS Code | Latest | https://code.visualstudio.com | Code editor |

### API Keys Required:
| Service | Purpose | Get It From |
|---------|---------|-------------|
| OpenAI GPT-4 | AI reasoning | https://platform.openai.com |
| Pinecone | Vector database | https://pinecone.io |
| (Optional) Claude API | Alternative AI | https://anthropic.com |

---

## 📁 Project Structure

```
medical-ai-project/
├── backend/                    # Python FastAPI server
│   ├── agents/                 # 7 AI Agents
│   │   ├── agent1_classifier.py        # Classifies report type
│   │   ├── agent2_lab_analyzer.py      # Analyzes blood tests
│   │   ├── agent3_imaging_analyzer.py  # Analyzes X-rays/imaging
│   │   ├── agent4_correlator.py        # Finds patterns across reports
│   │   ├── agent5_risk_predictor.py    # Calculates disease risk
│   │   ├── agent6_report_generator.py  # Patient-friendly report
│   │   └── agent7_recommendation.py    # Doctor recommendations
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── core/
│   │   ├── orchestrator.py     # Master controller of all agents
│   │   ├── database.py         # Database connections
│   │   └── config.py           # Settings & environment variables
│   ├── models/
│   │   └── schemas.py          # Data models
│   ├── utils/
│   │   ├── ocr_processor.py    # Extract text from scanned PDFs
│   │   ├── pdf_parser.py       # Parse PDF reports
│   │   └── encryption.py       # HIPAA-compliant encryption
│   └── main.py                 # App entry point
├── frontend/                   # React.js web interface
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Pages
│   │   └── App.jsx             # Main app
│   └── package.json
├── docker/
│   └── docker-compose.yml      # Run databases easily
├── .env.example                # Environment variables template
└── requirements.txt            # Python packages
```

---

## 🚀 Setup Instructions

### STEP 1: Install Python
1. Go to https://python.org/downloads
2. Download Python 3.11+
3. During install: ✅ CHECK "Add Python to PATH"
4. Open terminal/command prompt, type: `python --version`
5. Should show: `Python 3.11.x`

### STEP 2: Clone/Download Project
```bash
# Open terminal and run:
git clone <your-repo-url>
cd medical-ai-project
```

### STEP 3: Setup Python Environment
```bash
# Create virtual environment (keeps project packages separate)
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all Python packages:
pip install -r requirements.txt
```

### STEP 4: Setup Environment Variables
```bash
# Copy the example file:
cp .env.example .env

# Open .env in VS Code and fill in your API keys
```

### STEP 5: Start Databases with Docker
```bash
cd docker
docker-compose up -d
```

### STEP 6: Setup Frontend
```bash
cd frontend
npm install
```

### STEP 7: Run Everything
```bash
# Terminal 1 - Backend:
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend:
cd frontend
npm run dev
```

### STEP 8: Open in Browser
Go to: http://localhost:3000

---

## 🔑 API Keys Setup

### OpenAI API Key:
1. Go to https://platform.openai.com
2. Sign up / Login
3. Click "API Keys" in sidebar
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)
6. Paste in your `.env` file as: `OPENAI_API_KEY=sk-your-key-here`

### Pinecone API Key:
1. Go to https://pinecone.io
2. Sign up (free tier available)
3. Create a new index named "medical-reports"
4. Copy API key from dashboard
5. Paste in `.env` as: `PINECONE_API_KEY=your-key`

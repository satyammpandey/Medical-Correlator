# 🏥 MedAI Correlator

### Agentic AI-Powered Medical Report Correlator

### Early Disease Risk Predictor 

---

# 📋 About This Project

MedAI Correlator is an **Agentic AI system** that reads ALL your medical reports together — blood tests, eye checkups, kidney panels, X-rays, and doctor notes — and automatically connects the dots to detect hidden disease progression patterns that no single doctor sees.

🔴 **PROBLEM:**
When you visit multiple specialists, no one doctor has seen ALL your reports. Patterns that span months go undetected.

🟢 **SOLUTION:**
Our **7 AI Agents** analyze every report together, build value timelines, and alert you when a dangerous trend emerges.

⭐ **RESULT:**
Detected **Type 2 Diabetes progression 6–12 months before formal diagnosis** — with **89.3% confidence**.

---

# 🛠️ Technology Stack

## Backend

* Python 3.10
* FastAPI + Uvicorn
* Groq AI (Llama 3.3-70B Versatile)
* LangGraph + LangChain
* PostgreSQL
* Neo4j
* Redis
* SQLAlchemy + asyncpg
* PyMuPDF + pytesseract (OCR)
* aiofiles + loguru + pydantic-settings

## Frontend

* React.js + Vite
* Tailwind CSS
* Recharts
* Axios

## Infrastructure

* Docker + Docker Compose
* WSL 2 (required on Windows)

---

# 📁 Project Structure

```
medical-ai-project/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── agents/
│   ├── core/
│   ├── api/
│   └── utils/
├── frontend/
├── docker/
│   └── docker-compose.yml
└── start.bat
```

---

# 🚀 Setup Instructions

## STEP 1 — Install Required Software

| Software       | Version |
| -------------- | ------- |
| Python         | 3.10+   |
| Node.js        | 18+     |
| Docker Desktop | Latest  |
| Git            | Latest  |
| VS Code        | Latest  |

---

## STEP 2 — Clone Project

```
git clone https://github.com/YOUR-USERNAME/medai-correlator.git
cd medai-correlator
```

---

## STEP 3 — Configure Environment Variables

Create file:

```
backend/.env
```

Paste:

```
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile

DATABASE_URL=postgresql://postgres:password@localhost:5433/medical_db

NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

REDIS_URL=redis://localhost:6379/0

UPLOAD_DIR=./uploads

ALLOWED_ORIGINS=http://localhost:3000

DEBUG=True
```

---

## STEP 4 — Start Databases

```
cd docker
docker compose up -d
```

Services:

* Neo4j → http://localhost:7474
* PostgreSQL → port 5433
* Redis → port 6379

---

## STEP 5 — Setup Backend

```
cd backend

python -m venv venv

venv\Scripts\activate

pip install --upgrade pip

pip install fastapi uvicorn[standard]
pip install pydantic pydantic-settings loguru aiofiles

pip install groq langchain langchain-groq langgraph langchain-community

pip install sqlalchemy asyncpg redis neo4j

pip install pymupdf pytesseract pdf2image pillow

uvicorn main:app --reload --port 8000
```

API Docs:

```
http://localhost:8000/docs
```

---

## STEP 6 — Setup Frontend

Open new terminal:

```
cd frontend
npm install
npm run dev
```

Open browser:

```
http://localhost:3000
```

---

# 🤖 7 AI Agents

| Agent   | Function                 |
| ------- | ------------------------ |
| Agent 1 | Document classifier      |
| Agent 2 | Lab analyzer             |
| Agent 3 | Imaging analyzer         |
| Agent 4 | Cross report correlator  |
| Agent 5 | Risk predictor           |
| Agent 6 | Patient report generator |
| Agent 7 | Recommendation generator |

---

# 🔧 Common Errors Fix

| Error               | Fix                         |
| ------------------- | --------------------------- |
| ModuleNotFoundError | install missing package     |
| Docker not running  | start Docker Desktop        |
| Port 8000 busy      | kill python process         |
| DB connection error | restart docker              |
| Groq model error    | use llama-3.3-70b-versatile |

---

# 🧪 Test With Sample Reports

Upload test reports from:

```
/test_reports/
```

Expected output:

```
Risk: HIGH RISK Type 2 Diabetes
Confidence: 89.3%

Trend:
Glucose 110 → 118 → 122 mg/dL

Recommendation:
Consult Endocrinologist
Lifestyle modification
Medication guidance
```

---

# Disclaimer

This system is for research and academic demonstration only.
It is NOT a certified medical diagnostic tool.

Always consult a qualified doctor.

---

MedAI Correlator 

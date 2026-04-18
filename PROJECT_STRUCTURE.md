medical-ai-project/
│
├── 📄 README.md                          ← Complete setup guide
├── 📄 requirements.txt                   ← All Python packages
├── 📄 .env.example                       ← Environment variables template
├── 📄 start.sh                           ← One-click start (Mac/Linux)
├── 📄 start.bat                          ← One-click start (Windows)
│
├── 🐳 docker/
│   └── docker-compose.yml               ← PostgreSQL + Redis + Neo4j
│
├── 🐍 backend/
│   ├── main.py                          ← FastAPI app entry point
│   │
│   ├── core/
│   │   ├── config.py                    ← Settings & env variables
│   │   ├── database.py                  ← DB connections + tables
│   │   └── orchestrator.py             ← ⭐ Master AI Pipeline Controller
│   │
│   ├── agents/
│   │   ├── agent1_classifier.py         ← Document type classifier
│   │   ├── agent2_lab_analyzer.py       ← Blood test analyzer
│   │   ├── agent3_imaging_analyzer.py   ← X-ray/MRI analyzer
│   │   ├── agent4_correlator.py         ← ⭐ Cross-report pattern finder
│   │   ├── agent5_risk_predictor.py     ← Disease risk calculator
│   │   ├── agent6_report_generator.py   ← Patient-friendly report
│   │   └── agent7_recommendation.py     ← Doctor recommendations
│   │
│   ├── api/
│   │   └── routes.py                    ← All API endpoints
│   │
│   ├── models/
│   │   └── schemas.py                   ← All data models (Pydantic)
│   │
│   └── utils/
│       ├── pdf_parser.py               ← PDF text extraction
│       └── ocr_processor.py            ← Image OCR (Tesseract)
│
└── ⚛️  frontend/
    ├── package.json                     ← Node.js packages
    ├── vite.config.js                   ← React build config
    ├── tailwind.config.js               ← CSS framework config
    ├── index.html                       ← HTML entry point
    │
    └── src/
        ├── main.jsx                     ← React entry point
        ├── App.jsx                      ← App with routing
        ├── index.css                    ← Global styles
        │
        ├── pages/
        │   ├── Dashboard.jsx            ← Home page
        │   ├── UploadPage.jsx           ← File upload UI
        │   ├── ResultsPage.jsx          ← Analysis results
        │   └── DemoPage.jsx             ← Demo with sample data
        │
        └── components/
            └── Navbar.jsx               ← Navigation bar

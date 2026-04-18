#!/bin/bash
# ============================================
# START.SH - One-click startup script
# Run: chmod +x start.sh && ./start.sh
# ============================================

echo "🏥 Medical AI Correlator - Starting up..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found! Install Python 3.11+ from https://python.org"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Install from https://nodejs.org"
    exit 1
fi
echo "✅ Node found: $(node --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Databases won't start automatically."
    echo "   Install Docker from https://docker.com or set up databases manually."
else
    echo "✅ Docker found. Starting databases..."
    cd docker && docker-compose up -d && cd ..
    echo "✅ Databases started!"
fi

# Setup backend
echo ""
echo "📦 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate and install
source venv/bin/activate
pip install -r ../requirements.txt -q
echo "✅ Python packages installed"

# Check .env file
if [ ! -f "../.env" ]; then
    cp ../.env.example ../.env
    echo "⚠️  Created .env file from template."
    echo "   IMPORTANT: Edit .env and add your OpenAI API key!"
    echo "   Then run this script again."
    exit 1
fi

# Start backend in background
echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Setup and start frontend
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 Installing frontend packages (first time only, takes ~1 min)..."
    npm install
fi

echo ""
echo "🎨 Starting React frontend on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "════════════════════════════════════════"
echo "✅ EVERYTHING IS RUNNING!"
echo ""
echo "   🌐 Open in browser: http://localhost:3000"
echo "   📖 API Docs:        http://localhost:8000/docs"
echo "   🗄️  Neo4j Browser:   http://localhost:7474"
echo ""
echo "   Press Ctrl+C to stop everything"
echo "════════════════════════════════════════"

# Wait and cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait

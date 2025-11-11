#!/bin/bash

# 🚀 Quick Start Script for Gemini + OpenAI Setup
# This script will guide you through the setup process

set -e

echo "🎯 Aurea Orchestrator - Gemini Setup"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from template..."
    
    cat > .env << 'EOF'
# API Keys (Get from: https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

# Database
DATABASE_URL=postgresql://aurea:aurea_pass@localhost:5432/aurea_orchestrator

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Model Configuration
# Gemini models: gemini-1.5-pro, gemini-1.5-flash, gemini-pro
GEMINI_MODEL=gemini-1.5-flash
# OpenAI models: gpt-4, gpt-4-turbo, gpt-3.5-turbo
OPENAI_MODEL=gpt-4
COMPLEXITY_THRESHOLD=0.5
# Use gemini for simple tasks, openai for complex ones
DEFAULT_MODEL_PROVIDER=gemini

# App Configuration
DEBUG=true
LOG_LEVEL=INFO
EOF

    echo "✅ .env file created!"
    echo ""
fi

# Check API keys
echo "🔑 Checking API Keys..."
if grep -q "YOUR_GEMINI_API_KEY_HERE" .env; then
    echo "⚠️  Gemini API key not configured!"
    echo ""
    echo "📍 Get your Gemini API key from:"
    echo "   https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Enter your Gemini API key (or press Enter to skip): " gemini_key
    if [ ! -z "$gemini_key" ]; then
        sed -i "s|YOUR_GEMINI_API_KEY_HERE|$gemini_key|g" .env
        echo "✅ Gemini API key configured!"
    fi
fi

if grep -q "YOUR_OPENAI_API_KEY_HERE" .env; then
    echo "⚠️  OpenAI API key not configured!"
    echo ""
    echo "📍 Get your OpenAI API key from:"
    echo "   https://platform.openai.com/api-keys"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " openai_key
    if [ ! -z "$openai_key" ]; then
        sed -i "s|YOUR_OPENAI_API_KEY_HERE|$openai_key|g" .env
        echo "✅ OpenAI API key configured!"
    fi
fi

echo ""
echo "📦 Installing dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing Python packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Dependencies installed!"
echo ""

# Test Gemini connection
echo "🧪 Testing Gemini API connection..."
python3 << 'PYTHON_TEST'
import os
from dotenv import load_dotenv

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')

if google_api_key and google_api_key != 'YOUR_GEMINI_API_KEY_HERE':
    try:
        import google.generativeai as genai
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content('Say "Hello from Gemini!"')
        print(f"✅ Gemini API working! Response: {response.text}")
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
else:
    print("⚠️  Gemini API key not configured, skipping test")
PYTHON_TEST

echo ""
echo "🐳 Starting Docker services..."

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker and run this script again."
    exit 1
fi

# Start docker-compose services
docker-compose up -d postgres redis

echo "⏳ Waiting for services to be ready..."
sleep 5

# Initialize database
echo "🗄️  Initializing database..."
python3 << 'PYTHON_DB'
from aurea_orchestrator.database import init_db
try:
    init_db()
    print("✅ Database initialized!")
except Exception as e:
    print(f"⚠️  Database initialization: {e}")
PYTHON_DB

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Start the API server:"
echo "   docker-compose up"
echo ""
echo "2. Access the API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "3. Test with a simple task:"
echo '   curl -X POST http://localhost:8000/tasks/ \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '"'"'{"task_description": "Create a hello world function"}'"'"
echo ""
echo "4. View task status:"
echo "   curl http://localhost:8000/tasks/{task_id}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Documentation:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "- Quick Start:    QUICKSTART_REAL.md"
echo "- Gemini Setup:   SETUP_GEMINI.md"
echo "- Architecture:   ARCHITECTURE.md"
echo "- MVP Status:     MVP_STATUS.md"
echo ""
echo "💡 Tip: Gemini 1.5 Flash is 50x cheaper than GPT-4!"
echo "    Configure DEFAULT_MODEL_PROVIDER=gemini in .env"
echo ""

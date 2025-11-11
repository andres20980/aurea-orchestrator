#!/bin/bash
set -e

echo "🚀 Aurea Orchestrator - Quick Setup"
echo "===================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    exit 1
fi

echo "✅ Docker and Python found"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY)"
    echo ""
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo ""
echo "🐳 Starting services with Docker..."
echo ""

# Start Redis and PostgreSQL
docker-compose up -d redis postgres

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from aurea_orchestrator.database import init_db; init_db(); print('✅ Database initialized')"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📚 Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Start server: uvicorn aurea_orchestrator.main:app --reload"
echo "  4. In another terminal: celery -A aurea_orchestrator.celery_app worker --loglevel=info"
echo ""
echo "📖 Documentation: http://localhost:8000/docs"
echo ""

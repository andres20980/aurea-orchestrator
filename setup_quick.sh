#!/bin/bash
set -e

echo "🚀 Aurea Orchestrator - Quick Setup"
echo "===================================="
echo ""

# Check prerequisites
echo "📋 Verificando prerequisitos..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado."
    exit 1
fi

echo "✅ Docker y Python encontrados"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita .env y agrega tus API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY)"
    echo ""
fi

# Create virtual environment
echo "🐍 Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# Install dependencies
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo ""
echo "🐳 Iniciando servicios con Docker..."
echo ""

# Start Redis and PostgreSQL
docker-compose up -d redis postgres

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 5

# Initialize database
echo "🗄️  Inicializando base de datos..."
python3 -c "from aurea_orchestrator.database import init_db; init_db(); print('✅ Base de datos inicializada')"

echo ""
echo "🎉 Setup completado!"
echo ""
echo "📚 Próximos pasos:"
echo "  1. Edita .env y agrega tus API keys"
echo "  2. Ejecuta: source venv/bin/activate"
echo "  3. Inicia el servidor: uvicorn aurea_orchestrator.main:app --reload"
echo "  4. En otra terminal: celery -A aurea_orchestrator.celery_app worker --loglevel=info"
echo ""
echo "📖 Documentación: http://localhost:8000/docs"
echo ""

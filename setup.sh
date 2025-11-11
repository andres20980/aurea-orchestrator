#!/bin/bash
# Setup script for Aurea Orchestrator Sandbox

set -e

echo "========================================="
echo "Aurea Orchestrator Setup"
echo "========================================="
echo ""

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi
echo "✓ Docker is installed"

# Check Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi
echo "✓ Docker is running"

# Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+."
    exit 1
fi
echo "✓ Python 3 is installed"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Build Docker image
echo ""
echo "Building sandbox Docker image..."
docker build -t aurea-sandbox:latest .
echo "✓ Docker image built successfully"

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start the server, run:"
echo "  python src/main.py"
echo ""
echo "Or with Docker Compose:"
echo "  docker-compose up"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

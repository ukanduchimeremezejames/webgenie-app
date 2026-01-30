#!/bin/bash
# Development startup script

set -e

echo "🚀 WebGenie Backend - Development Setup"
echo "========================================"

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/results data/datasets logs

# Check Redis
echo "🔍 Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo "✓ Redis is running"
    else
        echo "⚠️  Redis is not running. Start with: redis-server"
    fi
else
    echo "⚠️  Redis CLI not found. Install Redis or use Docker: docker run -d -p 6379:6379 redis:7-alpine"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Redis (if not already running):"
echo "   docker run -d -p 6379:6379 redis:7-alpine"
echo ""
echo "2. Start the FastAPI server:"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "3. In another terminal, start Celery worker:"
echo "   celery -A app.workers.celery_app worker --loglevel=info"
echo ""
echo "4. Visit API docs:"
echo "   http://localhost:8000/api/docs"

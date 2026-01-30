@echo off
REM Windows Development Startup Script

echo.
echo 🚀 WebGenie Backend - Development Setup
echo ========================================

REM Check Python version
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating .env file...
    copy .env.example .env
)

REM Create data directories
echo 📁 Creating data directories...
if not exist "data\results" mkdir data\results
if not exist "data\datasets" mkdir data\datasets
if not exist "logs" mkdir logs

echo.
echo ✨ Setup complete!
echo.
echo Next steps:
echo 1. Start Redis (using Docker):
echo    docker run -d -p 6379:6379 redis:7-alpine
echo.
echo 2. Start the FastAPI server:
echo    python -m uvicorn app.main:app --reload
echo.
echo 3. In another terminal, start Celery worker:
echo    celery -A app.workers.celery_app worker --loglevel=info
echo.
echo 4. Visit API docs:
echo    http://localhost:8000/api/docs
echo.
pause

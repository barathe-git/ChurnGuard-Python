#!/bin/bash

# ChurnGuard Installation Script
echo "🚀 Installing ChurnGuard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p resources/models
mkdir -p resources/config

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Initialize database
echo "🗄️  Initializing database..."
python scripts/db_init.py

# Optimize database
echo "⚡ Optimizing database..."
python scripts/db_optimization.py

echo "✅ Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start Redis server: redis-server"
echo "3. Run the application: streamlit run app.py"
echo ""
echo "For API server: uvicorn app:app --host 0.0.0.0 --port 8000"
echo "For Celery worker: celery -A app.celery worker --loglevel=info"

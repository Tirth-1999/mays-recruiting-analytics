#!/bin/bash

# Edulytix Dashboard Startup Script

echo "🚀 Starting Edulytix Dashboard..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3.12 -m venv venv"
    echo "Then: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated (Python 3.12)"
echo ""

# Verify Python version
PYTHON_VERSION=$(python --version)
echo "Using: $PYTHON_VERSION"
echo ""

# Check if database exists
if [ ! -f "edulytix.db" ]; then
    echo "⚠️  Database not found. Running ETL pipeline first..."
    python etl_pipeline.py
    echo ""
fi

# Start Streamlit using venv's streamlit
echo "📊 Launching dashboard at http://localhost:8501"
echo "🌐 Live deployment available at: https://mays-recruiting-analytics.streamlit.app/"
echo ""
venv/bin/streamlit run main_app.py --server.port 8501

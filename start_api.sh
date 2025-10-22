#!/bin/bash

# Thai Model API Startup Script
# This script sets up and starts the Thai model API server

set -e  # Exit on error

echo "🚀 Thai Model API Startup"
echo "========================"

# Check if virtual environment exists
if [ ! -d "llm-env" ]; then
    echo "❌ Virtual environment not found"
    echo "Run: python -m venv llm-env && ./llm-env/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if model exists
if [ ! -d "models/qwen_thai_lora" ]; then
    echo "❌ Thai model not found at models/qwen_thai_lora"
    echo "Please run training first: ./manage.sh train"
    exit 1
fi

# Check if port is available
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8001 is already in use"
    echo "Stop existing server or use a different port"
    exit 1
fi

# Set environment variables
export PYTHONPATH="${PWD}:${PYTHONPATH}"
export CUDA_VISIBLE_DEVICES=0  # Use first GPU

echo "✅ Environment checks passed"
echo "📁 Model path: models/qwen_thai_lora"
echo "🐍 Python: $(./llm-env/bin/python --version)"
echo "🌐 Starting server on http://localhost:8001"
echo "📚 API docs: http://localhost:8001/docs"
echo ""

# Start the server
exec ./llm-env/bin/python src/hosting/fastapi_server.py

#!/bin/bash
# Quick setup script for Thai Language Model Project

echo "🇹🇭 Setting up Thai Language Model Project..."

# Check if virtual environment exists
if [ ! -d "llm-env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv llm-env
fi

# Activate and install dependencies
echo "Installing dependencies..."
source llm-env/bin/activate
pip install --upgrade pip
pip install -r config/requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To get started:"
echo "  source llm-env/bin/activate"
echo "  ./manage.sh help"
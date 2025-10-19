#!/bin/bash
# Simple launcher script for Ollama Chat GUI

echo "🚀 Launching Ollama Chat GUI..."

# Check if OLLAMA_HOST is set
if [ -z "$OLLAMA_HOST" ]; then
    echo "⚠️  OLLAMA_HOST not set. Setting to default localhost:11434"
    export OLLAMA_HOST=localhost:11434
fi

# Use the virtual environment Python
llm-env/bin/python chat_gui.py
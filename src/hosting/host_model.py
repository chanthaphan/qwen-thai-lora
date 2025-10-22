#!/usr/bin/env python3
"""
Host your fine-tuned Thai model using FastAPI + transformers
This script sets up a local API server for your Thai LoRA model
Note: vLLM doesn't support LoRA adapters directly, so we use transformers + FastAPI
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import transformers
        import peft
        import torch
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: ./llm-env/bin/pip install fastapi uvicorn[standard]")
        return False

def setup_thai_model_server():
    """Setup and run FastAPI server with your fine-tuned Thai model"""
    
    # Check if model exists
    model_path = "./models/qwen_thai_lora"
    if not Path(model_path).exists():
        print("❌ Thai LoRA model not found at ./models/qwen_thai_lora")
        print("Please run the training module first to create the model")
        return 1
    
    # Check for adapter files
    adapter_config = Path(model_path) / "adapter_config.json"
    if not adapter_config.exists():
        print("❌ LoRA adapter config not found")
        print("Make sure ./models/qwen_thai_lora contains adapter_config.json")
        return 1
    
    print("🚀 Starting FastAPI server with your Thai fine-tuned model...")
    print(f"📁 Model path: {model_path}")
    
    # Activate virtual environment and check dependencies
    venv_python = "./llm-env/bin/python"
    
    if not Path(venv_python).exists():
        print("❌ Virtual environment not found at ./llm-env")
        print("Please create it with: python -m venv llm-env")
        return 1
    
    # Check if FastAPI is installed
    check_cmd = [venv_python, "-c", "import fastapi, uvicorn; print('Dependencies OK')"]
    try:
        result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ FastAPI not installed in virtual environment")
            print("Install with: ./llm-env/bin/pip install fastapi uvicorn[standard]")
            return 1
    except subprocess.TimeoutExpired:
        print("❌ Dependency check timed out")
        return 1
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return 1
    
    print("✅ Dependencies checked successfully")
    
    # FastAPI command to serve the Thai model
    fastapi_command = [
        venv_python, "src/hosting/fastapi_server.py"
    ]
    
    print("🔧 Command:", " ".join(fastapi_command))
    print("🌐 Server will be available at: http://localhost:8001")
    print("📡 API endpoint: http://localhost:8001/v1/chat/completions")
    print("📝 Summarization: http://localhost:8001/v1/summarize")
    print("📚 API docs: http://localhost:8001/docs")
    print("🤖 Model name: thai-qwen-lora")
    print("\n💡 To test your hosted model:")
    print("   curl -X POST 'http://localhost:8001/v1/summarize' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"text\": \"ข้อความที่ต้องการสรุป\", \"max_tokens\": 100}'")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Run the FastAPI server
        subprocess.run(fastapi_command, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting FastAPI server: {e}")
        print("\n💡 Alternative: Try the Gradio interface:")
        print("   python thai_model_gui.py")
        return 1
    except FileNotFoundError:
        print("❌ Python not found or thai_model_api.py missing")
        print("Make sure thai_model_api.py exists in the current directory")
        return 1

if __name__ == "__main__":
    exit_code = setup_thai_model_server()
    sys.exit(exit_code)
#!/bin/bash
# Thai Language Model Project Manager
# Convenient script to manage common project tasks

set -e

PROJECT_ROOT="/home/chanthaphan/project"
VENV_PATH="$PROJECT_ROOT/llm-env/bin/python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    echo -e "${1}${2}${NC}"
}

print_header() {
    echo ""
    print_color $BLUE "================================================"
    print_color $BLUE "Thai Language Model Project Manager"
    print_color $BLUE "================================================"
    echo ""
}

print_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup           Set up the project environment"
    echo "  train           Run Thai model fine-tuning"
    echo "  test            Run model tests"
    echo "  test-simple     Run simple model test"
    echo "  host-gui        Start Gradio web interface"
    echo "  host-api        Start FastAPI server"
    echo "  host-vllm       Start vLLM inference server"
    echo "  chat-ollama     Start Ollama chat application"
    echo "  chat-vllm       Start vLLM chat application"
    echo "  chat-web        Start web-based multi-backend chat"
    echo "  merge-model     Merge LoRA with base model"
    echo "  docker-build    Build Docker image"
    echo "  docker-run      Run Docker container"
    echo "  status          Show project status"
    echo "  clean           Clean temporary files"
    echo "  help            Show this help message"
    echo ""
}

check_environment() {
    if [ ! -f "$VENV_PATH" ]; then
        print_color $RED "ERROR: Virtual environment not found at $VENV_PATH"
        print_color $YELLOW "Please run: $0 setup"
        exit 1
    fi
}

cmd_setup() {
    print_color $BLUE "Setting up project environment..."
    
    # Check if virtual environment exists
    if [ ! -d "$PROJECT_ROOT/llm-env" ]; then
        print_color $YELLOW "Creating virtual environment..."
        cd $PROJECT_ROOT
        python3 -m venv llm-env
    fi
    
    # Install dependencies
    print_color $YELLOW "Installing dependencies..."
    $VENV_PATH -m pip install --upgrade pip
    $VENV_PATH -m pip install -r config/requirements.txt
    
    print_color $GREEN "Environment setup completed!"
}

cmd_train() {
    print_color $BLUE "Starting Thai model fine-tuning..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/training/finetune_thai_model.py
}

cmd_test() {
    print_color $BLUE "Running comprehensive model tests..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/testing/test_model.py
}

cmd_test_simple() {
    print_color $BLUE "Running simple model test..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/testing/test_simple.py
}

cmd_host_gui() {
    print_color $BLUE "Starting Gradio web interface..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/interfaces/gradio_gui.py
}

cmd_host_api() {
    print_color $BLUE "Starting FastAPI server..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/hosting/fastapi_server.py
}

cmd_host_vllm() {
    print_color $BLUE "Starting vLLM inference server..."
    check_environment
    cd $PROJECT_ROOT
    
    # Check if merged model exists
    if [ -d "models/qwen_thai_lora_merged" ]; then
        MODEL_PATH="models/qwen_thai_lora_merged"
        print_color $GREEN "Using merged Thai model: $MODEL_PATH"
    else
        MODEL_PATH="Qwen/Qwen2.5-1.5B-Instruct"
        print_color $YELLOW "WARNING: Using base model (LoRA not merged): $MODEL_PATH"
        print_color $YELLOW "Run './manage.sh merge-model' first for Thai capabilities"
    fi
    
    print_color $BLUE "Starting vLLM server on port 8000..."
    print_color $YELLOW "This may take a few minutes to load the model..."
    $VENV_PATH -m vllm.entrypoints.openai.api_server \
        --model "$MODEL_PATH" \
        --host 0.0.0.0 \
        --port 8000 \
        --served-model-name thai-model
}

cmd_chat_ollama() {
    print_color $BLUE "Starting Ollama chat application..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/interfaces/ollama_chat.py
}

cmd_chat_vllm() {
    print_color $BLUE "Starting vLLM chat application..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/interfaces/vllm_chat.py
}

cmd_chat_web() {
    print_color $BLUE "Starting web-based multi-backend chat..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/interfaces/web_chat.py
}

cmd_merge_model() {
    print_color $BLUE "Merging LoRA with base model..."
    check_environment
    cd $PROJECT_ROOT
    $VENV_PATH src/training/merge_lora_model.py
}

cmd_docker_build() {
    print_color $BLUE "Building Docker image..."
    cd $PROJECT_ROOT
    docker build -f deployment/Dockerfile -t thai-model-api .
    print_color $GREEN "Docker image built successfully!"
}

cmd_docker_run() {
    print_color $BLUE "Running Docker container..."
    cd $PROJECT_ROOT
    docker run -p 8001:8001 --gpus all thai-model-api
}

cmd_status() {
    print_color $BLUE "Project Status"
    echo ""
    
    # Check virtual environment
    if [ -f "$VENV_PATH" ]; then
        print_color $GREEN "[OK] Virtual environment: Ready"
    else
        print_color $RED "[ERROR] Virtual environment: Not found"
    fi
    
    # Check models
    if [ -d "$PROJECT_ROOT/models/qwen_thai_lora" ]; then
        print_color $GREEN "[OK] Thai model: Available"
    else
        print_color $YELLOW "[WARNING] Thai model: Not trained yet"
    fi
    
    # Check dependencies
    if [ -f "$PROJECT_ROOT/config/requirements.txt" ]; then
        print_color $GREEN "[OK] Dependencies: Configured"
    else
        print_color $RED "[ERROR] Dependencies: Missing requirements.txt"
    fi
    
    # Show structure
    echo ""
    print_color $BLUE "Project Structure:"
    tree -L 2 $PROJECT_ROOT || ls -la $PROJECT_ROOT
}

cmd_clean() {
    print_color $BLUE "Cleaning temporary files..."
    cd $PROJECT_ROOT
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove temporary files
    rm -rf .pytest_cache 2>/dev/null || true
    rm -rf *.egg-info 2>/dev/null || true
    
    print_color $GREEN "Cleanup completed!"
}

# Main command handling
case "${1:-help}" in
    setup)
        print_header
        cmd_setup
        ;;
    train)
        print_header
        cmd_train
        ;;
    test)
        print_header
        cmd_test
        ;;
    test-simple)
        print_header
        cmd_test_simple
        ;;
    host-gui)
        print_header
        cmd_host_gui
        ;;
    host-api)
        print_header
        cmd_host_api
        ;;
    host-vllm)
        print_header
        cmd_host_vllm
        ;;
    chat-ollama)
        print_header
        cmd_chat_ollama
        ;;
    chat-vllm)
        print_header
        cmd_chat_vllm
        ;;
    chat-web)
        print_header
        cmd_chat_web
        ;;
    merge-model)
        print_header
        cmd_merge_model
        ;;
    docker-build)
        print_header
        cmd_docker_build
        ;;
    docker-run)
        print_header
        cmd_docker_run
        ;;
    status)
        print_header
        cmd_status
        ;;
    clean)
        print_header
        cmd_clean
        ;;
    help|*)
        print_header
        print_usage
        ;;
esac
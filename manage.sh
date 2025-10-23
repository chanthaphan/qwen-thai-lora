#!/bin/bash
# Thai Language Model Project Manager
# Simple and intuitive project management

set -e

PROJECT_ROOT="/home/chanthaphan/project"
VENV_PATH="$PROJECT_ROOT/llm-env/bin/python"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_color() {
    echo -e "${1}${2}${NC}"
}

print_header() {
    echo ""
    print_color $CYAN "🇹🇭 Thai Model Manager"
    echo ""
}

print_usage() {
    echo "Usage: ./manage.sh [COMMAND]"
    echo ""
    print_color $BLUE "🔧 Setup & Management:"
    echo "  setup           Install dependencies and set up environment"
    echo "  setup-openai    Set up OpenAI API key for GPT models"
    echo "  setup-postgres  Set up PostgreSQL for chat history"
    echo "  status          Show project and server status"
    echo "  clean           Clean temporary files and logs"
    echo ""
    print_color $BLUE "🤖 Model Operations:"
    echo "  train           Train the Thai model with LoRA"
    echo "  merge           Merge LoRA weights with base model"
    echo "  test            Test the trained model"
    echo ""
    print_color $BLUE "💬 Chat Interfaces:"
    echo "  chat            Interactive vLLM chat (recommended)"
    echo "  chat-ollama     Chat with Ollama models"
    echo "  chat-openai     Chat with OpenAI models (GPT-4, etc.)"
    echo "  chat-web        Web-based chat interface"
    echo "  chat-web-db     Web interface with PostgreSQL persistence"
    echo ""
    print_color $BLUE "🚀 Servers:"
    echo "  serve           Start vLLM server for Thai model"
    echo "  serve-api       Start FastAPI server"
    echo "  serve-gui       Start Gradio web interface"
    echo ""
    print_color $BLUE "📊 Server Management:"
    echo "  server status   Check server status"
    echo "  server start    Start vLLM server"
    echo "  server stop     Stop vLLM server"
    echo "  server restart  Restart vLLM server"
    echo "  server test     Test server connection"
    echo ""
    print_color $BLUE "🐳 Docker:"
    echo "  docker build    Build Docker image"
    echo "  docker run      Run Docker container"
    echo ""
    print_color $YELLOW "Examples:"
    echo "  ./manage.sh setup         # First time setup"
    echo "  ./manage.sh train         # Train Thai model"
    echo "  ./manage.sh serve         # Start server"
    echo "  ./manage.sh chat          # Start chatting"
    echo "  ./manage.sh chat-openai   # Chat with GPT-4 (requires API key)"
    echo "  ./manage.sh chat-web      # Web interface with all backends"
    echo "  ./manage.sh server status # Check if server is running"
    echo ""
}

check_environment() {
    if [ ! -f "$VENV_PATH" ]; then
        print_color $RED "❌ Environment not set up"
        print_color $YELLOW "💡 Run: ./manage.sh setup"
        exit 1
    fi
}

#===============================================================================
# SETUP & MANAGEMENT
#===============================================================================

cmd_setup() {
    print_color $BLUE "🔧 Setting up environment..."
    
    if [ ! -d "$PROJECT_ROOT/llm-env" ]; then
        print_color $YELLOW "📦 Creating virtual environment..."
        cd $PROJECT_ROOT
        python3 -m venv llm-env
    fi
    
    print_color $YELLOW "📥 Installing dependencies..."
    $VENV_PATH -m pip install --upgrade pip
    $VENV_PATH -m pip install -r config/requirements.txt
    
    print_color $GREEN "✅ Setup completed!"
    print_color $CYAN "💡 Next steps:"
    echo "  1. ./manage.sh train      # Train the model"
    echo "  2. ./manage.sh serve      # Start server"
    echo "  3. ./manage.sh chat       # Start chatting"
}

cmd_status() {
    print_color $BLUE "📊 Project Status"
    echo ""
    
    # Environment
    if [ -f "$VENV_PATH" ]; then
        print_color $GREEN "✅ Environment: Ready"
    else
        print_color $RED "❌ Environment: Not set up"
    fi
    
    # Models
    if [ -d "$PROJECT_ROOT/models/qwen_thai_lora" ]; then
        print_color $GREEN "✅ Thai LoRA: Available"
    else
        print_color $YELLOW "⚠️  Thai LoRA: Not trained"
    fi
    
    if [ -d "$PROJECT_ROOT/models/qwen_thai_merged" ]; then
        print_color $GREEN "✅ Merged Model: Available"
    else
        print_color $YELLOW "⚠️  Merged Model: Not created"
    fi
    
    # Server status
    echo ""
    print_color $BLUE "🚀 Server Status:"
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_color $GREEN "✅ vLLM Server: Running on port 8000"
        # Show model info
        model_info=$(curl -s http://localhost:8000/v1/models | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data['data']:
        model = data['data'][0]
        print(f\"   📋 Model: {model['id']}\")
        print(f\"   🔗 Root: {model['root']}\")
        print(f\"   📏 Max tokens: {model['max_model_len']:,}\")
except:
    pass
" 2>/dev/null)
        echo "$model_info"
    else
        print_color $RED "❌ vLLM Server: Not running"
    fi
    
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        print_color $GREEN "✅ API Server: Running on port 8001"
    else
        print_color $YELLOW "⚠️  API Server: Not running"
    fi
}

cmd_clean() {
    print_color $BLUE "🧹 Cleaning project..."
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean logs
    rm -f logs/*.log 2>/dev/null || true
    
    print_color $GREEN "✅ Cleanup completed!"
}

cmd_setup_openai() {
    print_color $BLUE "🔑 Setting up OpenAI API key..."
    cd "$PROJECT_ROOT"
    
    if [ -f "./scripts/setup/setup_openai_key.sh" ]; then
        ./scripts/setup/setup_openai_key.sh
    else
        print_color $RED "❌ OpenAI setup script not found!"
        echo "Please ensure setup_openai_key.sh exists in scripts/setup/ folder."
        exit 1
    fi
}

cmd_setup_postgres() {
    print_color $BLUE "🐘 Setting up PostgreSQL for chat history..."
    cd "$PROJECT_ROOT"
    
    if [ -f "./scripts/setup/setup_postgres_fixed.sh" ]; then
        ./scripts/setup/setup_postgres_fixed.sh
    elif [ -f "./scripts/setup/setup_postgres.sh" ]; then
        ./scripts/setup/setup_postgres.sh
    else
        print_color $RED "❌ PostgreSQL setup script not found!"
        echo "Please ensure setup_postgres_fixed.sh exists in scripts/setup/ folder."
        exit 1
    fi
}

#===============================================================================
# MODEL OPERATIONS
#===============================================================================

cmd_train() {
    print_color $BLUE "🏋️ Training Thai model..."
    check_environment
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.training.finetune_thai_model
}

cmd_merge() {
    print_color $BLUE "🔀 Merging LoRA with base model..."
    check_environment
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.training.merge_lora_model
}

cmd_test() {
    print_color $BLUE "🧪 Testing model..."
    check_environment
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.tests.test_model
}

#===============================================================================
# CHAT INTERFACES
#===============================================================================

cmd_chat() {
    print_color $BLUE "💬 Starting vLLM chat..."
    check_environment
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.interfaces.vllm_chat
}

cmd_chat_ollama() {
    print_color $BLUE "💬 Starting Ollama chat..."
    check_environment
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.interfaces.ollama_chat
}

cmd_chat_openai() {
    print_color $BLUE "💬 Starting OpenAI chat..."
    check_environment
    
    # Check if OpenAI API key is set
    if [ -z "$OPENAI_API_KEY" ]; then
        print_color $RED "❌ OpenAI API key not found"
        print_color $YELLOW "💡 Please set your OpenAI API key:"
        print_color $YELLOW "   export OPENAI_API_KEY='your-api-key-here'"
        print_color $YELLOW "💡 Get your API key from: https://platform.openai.com/api-keys"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.interfaces.openai_chat
}

cmd_chat_web() {
    print_color $BLUE "💬 Starting web chat interface..."
    check_environment
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.interfaces.web_chat
}

cmd_chat_web_db() {
    print_color $BLUE "💬 Starting web chat interface with PostgreSQL persistence..."
    check_environment
    
    # Check if database is configured
    if [ -f ".env" ]; then
        source .env
        print_color $GREEN "✅ Database configuration loaded"
    else
        print_color $YELLOW "⚠️  No .env file found - will use default database settings"
        print_color $YELLOW "💡 Run './manage.sh setup-postgres' to configure database"
    fi
    
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.interfaces.web_chat_db
}

#===============================================================================
# SERVERS
#===============================================================================

cmd_serve() {
    print_color $BLUE "🚀 Starting vLLM server..."
    exec ./scripts/manage_vllm.sh start
}

cmd_serve_api() {
    print_color $BLUE "🚀 Starting FastAPI server..."
    check_environment
    cd "$PROJECT_ROOT"
    $VENV_PATH scripts/api_server.py
}

cmd_serve_gui() {
    print_color $BLUE "🚀 Starting Gradio interface..."
    check_environment
    cd "$PROJECT_ROOT"
    $VENV_PATH -m thai_model.interfaces.gradio_gui
}

#===============================================================================
# SERVER MANAGEMENT
#===============================================================================

cmd_server() {
    case "$1" in
        status)
            exec ./scripts/manage_vllm.sh status
            ;;
        start)
            exec ./scripts/manage_vllm.sh start
            ;;
        stop)
            exec ./scripts/manage_vllm.sh stop
            ;;
        restart)
            exec ./scripts/manage_vllm.sh restart
            ;;
        test)
            exec ./scripts/manage_vllm.sh test
            ;;
        *)
            print_color $RED "❌ Unknown server command: $1"
            print_color $YELLOW "💡 Available: status, start, stop, restart, test"
            exit 1
            ;;
    esac
}

#===============================================================================
# DOCKER
#===============================================================================

cmd_docker_build() {
    print_color $BLUE "🐳 Building Docker image..."
    cd $PROJECT_ROOT
    docker build -f deployment/docker/Dockerfile -t thai-model-api .
    print_color $GREEN "✅ Docker image built!"
}

cmd_docker_run() {
    print_color $BLUE "🐳 Running Docker container..."
    cd $PROJECT_ROOT
    docker run -p 8001:8001 --gpus all thai-model-api
}

#===============================================================================
# MAIN COMMAND ROUTER
#===============================================================================

# Show header for all commands except help
if [[ "$1" != "help" && "$1" != "" ]]; then
    print_header
fi

case "$1" in
    # Setup & Management
    setup)
        cmd_setup
        ;;
    setup-openai)
        cmd_setup_openai
        ;;
    setup-postgres)
        cmd_setup_postgres
        ;;
    status)
        cmd_status
        ;;
    clean)
        cmd_clean
        ;;
    
    # Model Operations
    train)
        cmd_train
        ;;
    merge)
        cmd_merge
        ;;
    test)
        cmd_test
        ;;
    
    # Chat Interfaces
    chat)
        cmd_chat
        ;;
    chat-ollama)
        cmd_chat_ollama
        ;;
    chat-openai)
        cmd_chat_openai
        ;;
    chat-web)
        cmd_chat_web
        ;;
    chat-web-db)
        cmd_chat_web_db
        ;;
    
    # Servers
    serve)
        cmd_serve
        ;;
    serve-api)
        cmd_serve_api
        ;;
    serve-gui)
        cmd_serve_gui
        ;;
    
    # Server Management
    server)
        shift
        cmd_server "$@"
        ;;
    
    # Docker
    docker)
        case "$2" in
            build)
                cmd_docker_build
                ;;
            run)
                cmd_docker_run
                ;;
            *)
                print_color $RED "❌ Unknown docker command: $2"
                print_color $YELLOW "💡 Available: build, run"
                exit 1
                ;;
        esac
        ;;
    
    # Help and default
    help|"")
        print_header
        print_usage
        ;;
    
    *)
        print_header
        print_color $RED "❌ Unknown command: $1"
        echo ""
        print_usage
        exit 1
        ;;
esac
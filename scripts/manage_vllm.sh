#!/bin/bash
# vLLM Model Management Script
# ===========================

PROJECT_ROOT="/home/chanthaphan/project"
VENV_PATH="$PROJECT_ROOT/llm-env/bin/python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() {
    echo -e "${1}${2}${NC}"
}

print_header() {
    echo ""
    print_color $BLUE "================================================"
    print_color $BLUE "vLLM Model Management"
    print_color $BLUE "================================================"
    echo ""
}

show_model_status() {
    print_color $GREEN "📊 Current Model Status:"
    echo ""
    
    # Check available models
    if [ -d "models/qwen_thai_merged" ]; then
        print_color $GREEN "✅ Thai Merged Model: models/qwen_thai_merged"
        MODEL_SIZE=$(du -sh models/qwen_thai_merged | cut -f1)
        echo "   📦 Size: $MODEL_SIZE"
    else
        print_color $YELLOW "❌ Thai Merged Model: Not found"
    fi
    
    if [ -d "models/qwen_thai_lora" ]; then
        print_color $GREEN "✅ Thai LoRA Adapter: models/qwen_thai_lora"
        LORA_SIZE=$(du -sh models/qwen_thai_lora | cut -f1)
        echo "   📦 Size: $LORA_SIZE"
    else
        print_color $YELLOW "❌ Thai LoRA Adapter: Not found"
    fi
    
    # Check if vLLM server is running
    if pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null; then
        print_color $GREEN "🚀 vLLM Server: Running"
        VLLM_PID=$(pgrep -f "vllm.entrypoints.openai.api_server")
        echo "   🔢 PID: $VLLM_PID"
        echo "   🌐 Endpoint: http://localhost:8000"
    else
        print_color $YELLOW "⏹️  vLLM Server: Not running"
    fi
    
    echo ""
}

start_vllm() {
    print_color $BLUE "🚀 Starting vLLM server..."
    
    # Check if already running
    if pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null; then
        print_color $YELLOW "⚠️  vLLM server is already running!"
        print_color $BLUE "💡 Use 'stop' command to stop it first"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # Determine which model to use
    if [ -d "models/qwen_thai_merged" ]; then
        MODEL_PATH="models/qwen_thai_merged"
        print_color $GREEN "📦 Using Thai merged model: $MODEL_PATH"
    else
        MODEL_PATH="Qwen/Qwen2.5-1.5B-Instruct"
        print_color $YELLOW "⚠️  Using base model: $MODEL_PATH"
        print_color $YELLOW "💡 Merge LoRA first for Thai capabilities: ./manage.sh merge-model"
    fi
    
    print_color $BLUE "⏳ Loading model (this may take a few minutes)..."
    
    # Start vLLM server in background with custom parameters
    nohup $VENV_PATH -m vllm.entrypoints.openai.api_server \
        --model "$MODEL_PATH" \
        --host 0.0.0.0 \
        --port 8000 \
        --served-model-name thai-model \
        --max-model-len 4096 \
        --gpu-memory-utilization 0.8 \
        --dtype float16 > logs/vllm_server.log 2>&1 &
    
    # Wait a moment and check if it started
    sleep 5
    if pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null; then
        print_color $GREEN "✅ vLLM server started successfully!"
        print_color $BLUE "🌐 API endpoint: http://localhost:8000"
        print_color $BLUE "📚 Documentation: http://localhost:8000/docs"
        print_color $BLUE "📋 Logs: tail -f logs/vllm_server.log"
    else
        print_color $RED "❌ Failed to start vLLM server"
        print_color $BLUE "💡 Check logs: cat logs/vllm_server.log"
    fi
}

stop_vllm() {
    print_color $BLUE "⏹️  Stopping vLLM server..."
    
    VLLM_PID=$(pgrep -f "vllm.entrypoints.openai.api_server")
    if [ -n "$VLLM_PID" ]; then
        kill $VLLM_PID
        sleep 3
        
        # Force kill if still running
        if pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null; then
            print_color $YELLOW "⚠️  Force stopping..."
            pkill -9 -f "vllm.entrypoints.openai.api_server"
        fi
        
        print_color $GREEN "✅ vLLM server stopped"
    else
        print_color $YELLOW "⚠️  vLLM server is not running"
    fi
}

restart_vllm() {
    print_color $BLUE "🔄 Restarting vLLM server..."
    stop_vllm
    sleep 2
    start_vllm
}

test_vllm() {
    print_color $BLUE "🧪 Testing vLLM server..."
    
    if ! pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null; then
        print_color $RED "❌ vLLM server is not running"
        print_color $BLUE "💡 Start it first: $0 start"
        return 1
    fi
    
    # Test health endpoint
    print_color $YELLOW "📡 Testing health endpoint..."
    if curl -s http://localhost:8000/health > /dev/null; then
        print_color $GREEN "✅ Health check passed"
    else
        print_color $RED "❌ Health check failed"
        return 1
    fi
    
    # Test models endpoint
    print_color $YELLOW "📋 Available models:"
    curl -s http://localhost:8000/v1/models | jq '.data[0].id' || echo "thai-model"
    
    # Test chat completion
    print_color $YELLOW "💬 Testing chat completion..."
    RESPONSE=$(curl -s -X POST http://localhost:8000/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "thai-model",
            "messages": [{"role": "user", "content": "สวัสดี"}],
            "max_tokens": 50,
            "stream": false
        }')
    
    if echo "$RESPONSE" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
        print_color $GREEN "✅ Chat completion test passed"
        echo "📝 Response: $(echo "$RESPONSE" | jq -r '.choices[0].message.content')"
    else
        print_color $RED "❌ Chat completion test failed"
        echo "📝 Response: $RESPONSE"
    fi
}

show_logs() {
    print_color $BLUE "📋 vLLM Server Logs:"
    echo ""
    
    if [ -f "logs/vllm_server.log" ]; then
        tail -50 logs/vllm_server.log
    else
        print_color $YELLOW "⚠️  No log file found: logs/vllm_server.log"
    fi
}

configure_model() {
    print_color $BLUE "⚙️  Model Configuration Options:"
    echo ""
    echo "1. 🎯 Model Selection:"
    echo "   • Base Model: Qwen/Qwen2.5-1.5B-Instruct"
    echo "   • Thai Model: models/qwen_thai_merged (recommended)"
    echo ""
    echo "2. 🔧 Performance Tuning:"
    echo "   • GPU Memory: --gpu-memory-utilization 0.8"
    echo "   • Max Length: --max-model-len 4096"
    echo "   • Data Type: --dtype float16"
    echo ""
    echo "3. 🚀 Advanced Options:"
    echo "   • Tensor Parallel: --tensor-parallel-size 1"
    echo "   • Pipeline Parallel: --pipeline-parallel-size 1"
    echo "   • Quantization: --quantization awq|gptq"
    echo ""
    
    read -p "🔧 Edit vLLM configuration? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano "$0"  # Edit this script
    fi
}

show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status      Show current model and server status"
    echo "  start       Start vLLM server"
    echo "  stop        Stop vLLM server"
    echo "  restart     Restart vLLM server"
    echo "  test        Test vLLM server functionality"
    echo "  logs        Show server logs"
    echo "  config      Configure model parameters"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status         # Check if server is running"
    echo "  $0 start          # Start the server"
    echo "  $0 test           # Test API endpoints"
    echo "  $0 logs           # View recent logs"
    echo ""
}

# Main script logic
case "${1:-status}" in
    status)
        print_header
        show_model_status
        ;;
    start)
        print_header
        start_vllm
        ;;
    stop)
        print_header
        stop_vllm
        ;;
    restart)
        print_header
        restart_vllm
        ;;
    test)
        print_header
        test_vllm
        ;;
    logs)
        print_header
        show_logs
        ;;
    config)
        print_header
        configure_model
        ;;
    help|--help|-h)
        print_header
        show_usage
        ;;
    *)
        print_color $RED "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
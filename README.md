# 🇹🇭 Thai Language Model with LoRA Fine-tuning

**A production-ready Thai language model based on Qwen2.5-1.5B-Instruct with LoRA fine-tuning capabilities, multiple inference backends, and comprehensive deployment options.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](deployment/docker/)
[![vLLM](https://img.shields.io/badge/vLLM-Optimized-orange.svg)](https://github.com/vllm-project/vllm)

## 🌟 Features

### 🧠 **Advanced AI Capabilities**
- **Thai-specialized Model** fine-tuned from Qwen2.5-1.5B-Instruct
- **LoRA Fine-tuning** for efficient parameter adaptation
- **Multi-backend Support** (vLLM, Ollama, local inference)
- **Thai Language Optimization** with specialized tokenization

### 🚀 **Production Infrastructure**
- **vLLM Server** for high-performance inference (up to 32K tokens)
- **FastAPI Endpoints** with OpenAI-compatible API
- **Real-time Streaming** responses for interactive applications
- **Multiple Chat Interfaces** (CLI, Web, GUI)

### �️ **Developer Experience**
- **One-command Management** with intuitive `./manage.sh` script
- **Comprehensive Testing** and validation tools
- **Docker Deployment** ready for production
- **Modular Architecture** for easy customization

### � **User Interfaces**
- **Command-line Chat** for quick interactions
- **Web Interface** with Gradio for browser access
- **Multi-backend Chat** supporting vLLM and Ollama
- **API Integration** for custom applications

## 🚀 Quick Start

### **1. Clone and Setup**
```bash
git clone https://github.com/chanthaphan/qwen-thai-lora.git
cd qwen-thai-lora

# One-command setup
./manage.sh setup
```

### **2. Train Thai Model** 
```bash
# Train the Thai LoRA adapter
./manage.sh train

# Merge LoRA with base model for optimal performance
./manage.sh merge
```

### **3. Start Inference Server**
```bash
# Start vLLM server (recommended for production)
./manage.sh serve

# Or start other servers
./manage.sh serve-api    # FastAPI server
./manage.sh serve-gui    # Gradio web interface
```

### **4. Start Chatting**
```bash
# Interactive chat with Thai model
./manage.sh chat

# Or try other interfaces
./manage.sh chat-web     # Web-based chat
./manage.sh chat-ollama  # Ollama backend
```

### **5. Check Status**
```bash
./manage.sh status       # Complete project status
./manage.sh server status # Server status only
```

## 📋 Table of Contents

1. [Installation](#-installation)
2. [Project Structure](#-project-structure)
3. [Management Commands](#-management-commands)
4. [Usage Examples](#-usage-examples)
5. [API Documentation](#-api-documentation)
6. [Model Information](#-model-information)
7. [Deployment](#-deployment)
8. [Development](#-development)

## 📦 Installation

### **Prerequisites**
- Python 3.8+ (3.12 recommended)
- CUDA-compatible GPU (optional, for training and faster inference)
- 8GB+ RAM (16GB+ recommended)
- Docker (optional, for containerized deployment)

### **Automatic Setup**
```bash
# Clone repository
git clone https://github.com/chanthaphan/qwen-thai-lora.git
cd qwen-thai-lora

# Install everything with one command
./manage.sh setup
```

This will:
- Create virtual environment (`llm-env/`)
- Install all dependencies from `config/requirements.txt`
- Set up project structure
- Download base model if needed

### **Manual Installation**
```bash
# Create virtual environment
python3 -m venv llm-env
source llm-env/bin/activate

# Install dependencies
pip install -r config/requirements.txt
```

## 🏗️ Project Structure

```
qwen-thai-lora/
├── 📄 README.md                          # This file
├── 📄 pyproject.toml                     # Modern Python project configuration
├── 📄 setup.sh                           # Quick setup script
├── 📄 manage.sh                          # 🎯 Main project manager (simplified!)
├── 📄 QUICK_START.md                     # Quick start guide
├── 📄 LEARNING_PATH.md                   # Learning modules guide
│
├── 🐍 thai_model/                        # Main Python package
│   ├── __init__.py                       # Package initialization
│   ├── core/                             # Core model functionality
│   │   ├── __init__.py
│   │   ├── model.py                      # ThaiModel class
│   │   └── config.py                     # Configuration management
│   ├── api/                              # REST API server
│   │   ├── __init__.py
│   │   └── server.py                     # FastAPI application
│   ├── interfaces/                       # User interfaces
│   │   ├── __init__.py
│   │   ├── vllm_chat.py                  # vLLM chat interface 
│   │   ├── ollama_chat.py                # Ollama chat interface
│   │   ├── web_chat.py                   # Multi-backend web chat
│   │   └── gradio_gui.py                 # Gradio web interface
│   ├── training/                         # Training pipeline
│   │   ├── __init__.py
│   │   ├── finetune_thai_model.py        # LoRA fine-tuning
│   │   └── merge_lora_model.py           # Model merging
│   ├── tests/                            # Test suite
│   │   ├── __init__.py
│   │   ├── test_model.py                 # Model functionality tests
│   │   └── test_simple.py                # Simple validation tests
│   └── utils/                            # Utilities
│       ├── __init__.py
│       └── helpers.py                    # Helper functions
│
├── 📁 scripts/                           # Executable scripts
│   ├── api_server.py                     # API server launcher
│   ├── manage_vllm.sh                    # vLLM server management
│   ├── start_api.sh                      # API server starter
│   └── launch_gui.sh                     # GUI launcher
│
├── 📁 config/                            # Configuration files
│   ├── requirements.txt                  # Python dependencies
│   ├── model_config.yaml                 # Model configuration
│   ├── training_config.yaml              # Training parameters
│   └── sample_conversation.json          # Sample data
│
├── 📁 models/                            # Model files and checkpoints
│   ├── qwen_thai_lora/                   # Thai LoRA adapter (163MB)
│   │   ├── adapter_config.json
│   │   ├── adapter_model.safetensors
│   │   └── ...
│   └── qwen_thai_merged/                 # Merged Thai model (2.9GB)
│       ├── config.json
│       ├── model.safetensors.index.json
│       └── ...
│
├── 📁 deployment/                        # Deployment configurations
│   ├── docker/                           # Docker files
│   │   ├── Dockerfile                    # Main Dockerfile (GPU)
│   │   ├── Dockerfile.cpu                # CPU-only Dockerfile
│   │   ├── docker-compose.yml            # Development setup
│   │   ├── docker-compose.prod.yml       # Production setup
│   │   └── docker-demo.sh                # Demo script
│   ├── kubernetes/                       # Kubernetes manifests
│   ├── nginx/                            # Nginx configuration
│   ├── monitoring/                       # Monitoring (Prometheus)
│   └── systemd/                          # Systemd service files
│
├── 📁 docs/                              # Documentation
│   ├── README.md                         # Documentation index
│   ├── HOSTING_GUIDE.md                  # Hosting and deployment
│   ├── TRAINING_SUMMARY.md               # Training guide
│   ├── VLLM_MANAGEMENT.md                # vLLM management guide
│   └── MANAGE_RESTRUCTURE.md             # Management script guide
│
├── 📁 examples/                          # Usage examples
│   └── integration_examples/             # Integration samples
│
├── 📁 learning/                          # Learning modules
│   ├── learn.py                          # Learning system
│   ├── progress_tracker.py               # Progress tracking
│   └── module_*.py                       # Individual learning modules
│
├── 📁 data/                              # Data directory
│   ├── raw/                              # Raw datasets
│   ├── processed/                        # Processed datasets
│   └── samples/                          # Sample data
│
├── 📁 logs/                              # Log files
│   └── *.log                             # Application logs
│
└── 📁 llm-env/                           # Virtual environment
    ├── bin/python                        # Python interpreter
    ├── lib/                              # Installed packages
    └── ...                               # Environment files
```

## 🎯 Management Commands

The `./manage.sh` script provides intuitive commands organized by function:

### **🔧 Setup & Management**
```bash
./manage.sh setup           # Install dependencies and set up environment
./manage.sh status          # Show comprehensive project and server status
./manage.sh clean           # Clean temporary files and logs
```

### **🤖 Model Operations**
```bash
./manage.sh train           # Train the Thai LoRA adapter
./manage.sh merge           # Merge LoRA weights with base model  
./manage.sh test            # Test the trained model
```

### **💬 Chat Interfaces**
```bash
./manage.sh chat            # Interactive vLLM chat (recommended)
./manage.sh chat-ollama     # Chat with Ollama models
./manage.sh chat-web        # Web-based multi-backend chat
```

### **🚀 Server Management**
```bash
./manage.sh serve           # Start vLLM server for Thai model
./manage.sh serve-api       # Start FastAPI server  
./manage.sh serve-gui       # Start Gradio web interface

# Advanced server management
./manage.sh server status   # Check server status
./manage.sh server start    # Start vLLM server
./manage.sh server stop     # Stop vLLM server
./manage.sh server restart  # Restart vLLM server
./manage.sh server test     # Test server connection
```

### **🐳 Docker Commands**
```bash
./manage.sh docker build    # Build Docker image
./manage.sh docker run      # Run Docker container
```

### **📊 Status Display Example**
```bash
$ ./manage.sh status

🇹🇭 Thai Model Manager

📊 Project Status

✅ Environment: Ready
✅ Thai LoRA: Available
✅ Merged Model: Available

🚀 Server Status:
✅ vLLM Server: Running on port 8000
   📋 Model: thai-model
   🔗 Root: Qwen/Qwen2.5-1.5B-Instruct
   📏 Max tokens: 32,768
⚠️  API Server: Not running
```

## 💻 Usage Examples

### **Basic Chat Usage**

```bash
# Start vLLM server
./manage.sh serve

# Interactive chat
./manage.sh chat
```

Example conversation:
```
🤖 Using model: thai-model
🧠 Reasoning mode: OFF
📡 Streaming mode: ON

You: สวัสดี มีอะไรให้ช่วยไหม
🤖 Bot: สวัสดีค่ะ/ครับ! ฉันยินดีที่ได้รู้จักคุณและช่วยเหลือในสิ่งที่คุณต้องการ 
อย่าลังเลที่จะถามคำถามหรือขอความช่วยเหลือในเรื่องต่าง ๆ ค่ะ/ครับ

You: อธิบายเรื่องปัญญาประดิษฐ์ให้ฟังหน่อย
🤖 Bot: ปัญญาประดิษฐ์ (Artificial Intelligence หรือ AI) คือ...
```

### **API Usage**

```python
import requests

# Chat completion
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "thai-model",
        "messages": [
            {"role": "user", "content": "สวัสดี เป็นอย่างไรบ้าง"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
)
print(response.json())
```

### **Programmatic Model Usage**

```python
from thai_model.interfaces.vllm_chat import VLLMChat

# Initialize chat client
chat = VLLMChat()

# Send message
response = chat.send_message("สวัสดี")
print(response)

# Chat with conversation history
chat.conversation_history.append({"role": "user", "content": "ชื่อฉันคือจอห์น"})
response = chat.send_message("ฉันชื่ออะไร")
print(response)  # Should remember the name
```

### **Web Interface Usage**

```bash
# Start web interface
./manage.sh chat-web

# Or use Gradio GUI
./manage.sh serve-gui
```

Visit `http://localhost:7860` for the web interface with features:
- Multiple backend selection (vLLM, Ollama)
- Real-time streaming responses
- Conversation history
- Model switching
- Export/import conversations

### **Training Custom Model**

```bash
# Train Thai LoRA adapter
./manage.sh train

# Merge LoRA with base model for production
./manage.sh merge

# Test the trained model
./manage.sh test
```

### **Server Management**

```bash
# Check server status
./manage.sh server status

# Start/stop server
./manage.sh server start
./manage.sh server stop

# Test server connection
./manage.sh server test
```

## 📚 API Documentation

### **vLLM Server Endpoints (Port 8000)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/v1/models` | List available models |
| POST | `/v1/chat/completions` | OpenAI-compatible chat |

### **FastAPI Server Endpoints (Port 8001)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/predict` | Text generation |

### **Chat Completions (vLLM)**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-model",
    "messages": [
      {"role": "user", "content": "สวัสดี"}
    ],
    "max_tokens": 100,
    "temperature": 0.7,
    "stream": false
  }'
```

### **Streaming Response**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-model",
    "messages": [
      {"role": "user", "content": "เล่าเรื่องสั้น"}
    ],
    "max_tokens": 200,
    "stream": true
  }'
```

### **Available Models**

```bash
curl http://localhost:8000/v1/models
```

Response:
```json
{
  "object": "list",
  "data": [
    {
      "id": "thai-model",
      "object": "model",
      "root": "Qwen/Qwen2.5-1.5B-Instruct",
      "max_model_len": 32768
    }
  ]
}
```

## 🤖 Model Information

### **Base Model**
- **Name**: Qwen/Qwen2.5-1.5B-Instruct
- **Parameters**: 1.5 billion
- **Context Length**: 32,768 tokens
- **Architecture**: Transformer decoder

### **Thai LoRA Adapter**
- **Size**: 163MB
- **Rank**: 16
- **Alpha**: 32
- **Target Modules**: Query, Key, Value, Output projections
- **Training**: Thai conversation data

### **Merged Model**
- **Size**: 2.9GB
- **Optimization**: Combined base model + Thai LoRA
- **Performance**: Optimized for Thai language tasks
- **Deployment**: Production-ready with vLLM

### **Performance Characteristics**
- **Inference Speed**: ~50-100 tokens/second (GPU)
- **Memory Usage**: ~4GB VRAM (FP16)
- **Latency**: <100ms first token (warm)
- **Throughput**: High with vLLM batching

### **Supported Features**
- ✅ Thai language understanding
- ✅ English-Thai translation
- ✅ Conversation and chat
- ✅ Text generation
- ✅ Question answering
- ✅ Reasoning tasks

## 🐳 Deployment

### **Docker Deployment**

```bash
# Build production image
cd deployment/docker
docker build -f Dockerfile -t thai-model-api .

# Run container with GPU support
docker run -d -p 8000:8000 \
  --gpus all \
  -v ./models:/app/models:ro \
  -v ./config:/app/config:ro \
  thai-model-api

# Or use simplified commands
./manage.sh docker build
./manage.sh docker run
```

### **Docker Compose**

```bash
# Development setup
docker-compose up -d

# Production setup with monitoring
docker-compose -f docker-compose.prod.yml up -d
```

This includes:
- vLLM server with GPU acceleration
- FastAPI server
- Nginx reverse proxy
- Prometheus monitoring
- Grafana dashboards

### **Manual Deployment**

```bash
# Install dependencies
./manage.sh setup

# Train and merge model
./manage.sh train
./manage.sh merge

# Start production server
./manage.sh serve
```

### **Environment Variables**

```bash
# vLLM Configuration
export VLLM_MODEL_PATH="models/qwen_thai_merged"
export VLLM_HOST="0.0.0.0"
export VLLM_PORT="8000"
export VLLM_GPU_MEMORY_UTILIZATION="0.8"

# API Configuration
export API_HOST="0.0.0.0" 
export API_PORT="8001"
export LOG_LEVEL="INFO"
```

### **Systemd Service**

```bash
# Install systemd service
sudo cp deployment/systemd/thai-model-api.service /etc/systemd/system/
sudo systemctl enable thai-model-api
sudo systemctl start thai-model-api
```

### **Nginx Configuration**

```bash
# Install nginx config
sudo cp deployment/nginx/thai-model-api.nginx /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/thai-model-api.nginx /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## 🛠️ Development

### **Development Setup**

```bash
# Clone and setup
git clone https://github.com/chanthaphan/qwen-thai-lora.git
cd qwen-thai-lora
./manage.sh setup

# Run in development mode
./manage.sh serve    # vLLM server
./manage.sh chat     # Test chat
```

### **Code Structure**

The project follows a modular architecture:

- **`thai_model/core/`**: Core model functionality
- **`thai_model/interfaces/`**: User interaction layers
- **`thai_model/training/`**: Model training and fine-tuning
- **`thai_model/api/`**: REST API server
- **`scripts/`**: Utility and management scripts

### **Testing**

```bash
# Run model tests
./manage.sh test

# Test specific components
python -m thai_model.tests.test_model
python -m thai_model.tests.test_simple

# Test server functionality
./manage.sh server test
```

### **Adding New Features**

1. **New Interface**: Add to `thai_model/interfaces/`
2. **New Training**: Add to `thai_model/training/`
3. **New API Endpoint**: Add to `thai_model/api/`
4. **New Script**: Add to `scripts/` and update `manage.sh`

### **Learning System**

The project includes a comprehensive learning system:

```bash
# Access learning modules
cd learning/
python learn.py                    # Interactive learning
python progress_tracker.py         # Track progress
python module_1_1_package_architecture.py  # Specific modules
```

### **Configuration Management**

Edit configuration files in `config/`:

- **`model_config.yaml`**: Model parameters
- **`training_config.yaml`**: Training configuration
- **`requirements.txt`**: Python dependencies

## 📊 Performance & Monitoring

### **Server Monitoring**

```bash
# Real-time status
./manage.sh status
./manage.sh server status

# Check logs
tail -f logs/*.log

# Monitor GPU usage
nvidia-smi -l 1
```

### **Performance Metrics**

- **vLLM Server**: High-throughput inference with batching
- **Thai Model**: Optimized for Thai language tasks
- **Memory**: ~4GB VRAM for inference
- **Speed**: 50-100 tokens/second on modern GPU

### **Optimization Tips**

1. **Use merged model** for best performance
2. **Enable GPU acceleration** with CUDA
3. **Adjust batch size** based on available memory
4. **Use vLLM** for production inference
5. **Monitor resource usage** with provided tools

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### **Contributing Workflow**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes: `./manage.sh test`
5. Submit a pull request

### **Areas for Contribution**

- 🐛 **Bug fixes** and improvements
- 📚 **Documentation** enhancements  
- 🌐 **Internationalization** for other languages
- 🚀 **Performance optimizations**
- 🧪 **Testing** and validation
- 🔧 **New features** and interfaces

### **Development Guidelines**

- Follow Python PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for changes
- Use the `./manage.sh` script for consistency

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Qwen Team** for the excellent base model (Qwen2.5-1.5B-Instruct)
- **vLLM Team** for high-performance inference engine
- **Hugging Face** for transformers library and model hosting
- **Thai NLP Community** for datasets and language resources
- **Contributors** who help improve this project

## 📞 Support & Resources

- **📖 Documentation**: [docs/](docs/) folder
- **🐛 Issues**: [GitHub Issues](https://github.com/chanthaphan/qwen-thai-lora/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/chanthaphan/qwen-thai-lora/discussions)
- **🚀 Quick Start**: [QUICK_START.md](QUICK_START.md)
- **📚 Learning**: [LEARNING_PATH.md](LEARNING_PATH.md)

## 🎯 Next Steps

After setting up the project:

1. **Train your model**: `./manage.sh train`
2. **Start the server**: `./manage.sh serve`
3. **Try chatting**: `./manage.sh chat`
4. **Explore the API**: Check `http://localhost:8000/docs`
5. **Deploy to production**: Use Docker or manual deployment

---

**🇹🇭 Built with ❤️ for the Thai language AI community**

*Empowering Thai language processing with modern AI technology*
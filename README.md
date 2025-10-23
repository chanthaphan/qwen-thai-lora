# 🇹🇭 Thai Language Model - Restructured

**A comprehensive, production-ready Thai language model package with fine-tuning, hosting, and inference capabilities.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](deployment/docker/)

## 🌟 Features

### 🧠 **AI & Machine Learning**
- **Fine-tuned Thai Language Model** based on Qwen2.5-1.5B-Instruct
- **LoRA (Low-Rank Adaptation)** for efficient fine-tuning
- **Thai text summarization** with specialized tokenization
- **Multi-modal inference** supporting various generation tasks

### 🚀 **Production-Ready API**
- **FastAPI server** with OpenAI-compatible endpoints
- **Streaming responses** for real-time generation
- **Automatic documentation** with Swagger/OpenAPI
- **Health monitoring** and metrics collection

### 🖥️ **User Interfaces**
- **Command-line interface** for quick interactions
- **Web GUI** with Gradio for browser-based usage
- **REST API** for programmatic integration
- **Chat interfaces** for conversational AI

### 🐳 **DevOps & Deployment**
- **Docker containerization** with multi-stage builds
- **Kubernetes manifests** for scalable deployment
- **Nginx reverse proxy** configuration
- **Monitoring stack** with Prometheus and Grafana

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Installation](#-installation) 
3. [Project Structure](#-project-structure)
4. [Usage Examples](#-usage-examples)
5. [Configuration](#-configuration)
6. [API Documentation](#-api-documentation)
7. [Deployment](#-deployment)
8. [Development](#-development)
9. [Contributing](#-contributing)

## 🚀 Quick Start

### **1. Installation**

```bash
# Clone repository
git clone https://github.com/username/thai-language-model.git
cd thai-language-model

# Install package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### **2. Run API Server**

```bash
# Using the package
thai-model-api

# Or using script directly
python scripts/api_server.py --port 8001
```

### **3. Test the API**

```bash
# Health check
curl http://localhost:8001/health

# Chat completion
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-model",
    "messages": [{"role": "user", "content": "สวัสดี"}],
    "max_tokens": 50
  }'
```

### **4. Web Interface**

```bash
# Start web GUI
python scripts/chat_web.py
```

Visit `http://localhost:7860` for the web interface.

## 📦 Installation

### **Prerequisites**

- Python 3.8 or higher
- CUDA-compatible GPU (optional, for faster inference)
- Docker (optional, for containerized deployment)

### **Install from Source**

```bash
# Clone repository
git clone https://github.com/username/thai-language-model.git
cd thai-language-model

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

### **Install with Docker**

```bash
# Build Docker image
cd deployment/docker
docker build -f Dockerfile.cpu -t thai-model-api .

# Run container
docker run -d -p 8001:8001 thai-model-api
```

### **GPU Support**

For GPU acceleration, ensure you have:

```bash
# Install GPU version of PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For Docker GPU support
# Use Dockerfile instead of Dockerfile.cpu
docker build -t thai-model-api .
```

## 🏗️ Project Structure

```
thai-language-model/
├── 📄 README.md                          # This file
├── 📄 pyproject.toml                     # Modern Python project configuration
├── 📄 requirements.txt                   # Python dependencies
├── 📄 LICENSE                            # MIT License
├── 
├── 🐍 thai_model/                        # Main Python package
│   ├── __init__.py                       # Package initialization
│   ├── core/                             # Core model functionality
│   │   ├── model.py                      # ThaiModel class
│   │   ├── config.py                     # Configuration classes
│   │   └── tokenizer.py                  # Thai tokenization utilities
│   ├── api/                              # REST API server
│   │   ├── fastapi_server.py             # FastAPI application
│   │   ├── models.py                     # Pydantic request/response models
│   │   └── routes/                       # API route definitions
│   ├── interfaces/                       # User interfaces
│   │   ├── cli.py                        # Command-line interface
│   │   ├── web.py                        # Web GUI interface
│   │   └── chat.py                       # Chat functionality
│   ├── training/                         # Training pipeline
│   │   ├── trainer.py                    # Model training logic
│   │   ├── data_loader.py                # Dataset handling
│   │   └── evaluation.py                 # Model evaluation
│   ├── utils/                            # Utilities
│   │   ├── logger.py                     # Logging configuration
│   │   ├── helpers.py                    # Helper functions
│   │   └── validation.py                 # Input validation
│   └── tests/                            # Test suite
│       ├── test_core.py                  # Core functionality tests
│       ├── test_api.py                   # API endpoint tests
│       └── fixtures/                     # Test data and fixtures
├── 
├── 📁 scripts/                           # Executable scripts
│   ├── api_server.py                     # API server launcher
│   ├── train_model.py                    # Training script
│   ├── chat_cli.py                       # CLI chat application
│   └── chat_web.py                       # Web chat application
├── 
├── 📁 config/                            # Configuration files
│   ├── model_config.yaml                 # Model configuration
│   ├── training_config.yaml              # Training parameters
│   └── logging_config.yaml               # Logging configuration
├── 
├── 📁 deployment/                        # Deployment configurations
│   ├── docker/                           # Docker files
│   │   ├── Dockerfile                    # Main Dockerfile (GPU)
│   │   ├── Dockerfile.cpu                # CPU-only Dockerfile
│   │   ├── docker-compose.yml            # Multi-service setup
│   │   └── docker-demo.sh                # Deployment demo script
│   ├── kubernetes/                       # Kubernetes manifests
│   ├── nginx/                            # Nginx configuration
│   └── monitoring/                       # Monitoring configuration
├── 
├── 📁 docs/                              # Documentation
│   ├── installation.md                   # Installation guide
│   ├── usage.md                          # Usage examples
│   ├── api_reference.md                  # API documentation
│   └── deployment_guide.md               # Deployment guide
├── 
├── 📁 examples/                          # Usage examples
│   ├── basic_usage.py                    # Basic model usage
│   ├── custom_training.py                # Custom training example
│   └── api_client.py                     # API client example
├── 
├── 📁 data/                              # Data directory
│   ├── raw/                              # Raw datasets
│   ├── processed/                        # Processed datasets
│   └── samples/                          # Sample data
├── 
└── 📁 models/                            # Model files
    ├── base/                             # Base model files
    ├── checkpoints/                      # Training checkpoints
    └── exports/                          # Exported models
```

## 💻 Usage Examples

### **Basic Model Usage**

```python
from thai_model import ThaiModel, ModelConfig

# Initialize model
config = ModelConfig.from_yaml("config/model_config.yaml")
model = ThaiModel(config)

# Generate text
response = model.generate_text("สวัสดี ท่านเป็นอย่างไรบ้าง")
print(response)

# Chat completion
messages = [
    {"role": "user", "content": "อธิบายเรื่องปัญญาประดิษฐ์"}
]
response = model.chat_completion(messages)
print(response)

# Text summarization
text = "ข่าวยาว ๆ ที่ต้องการสรุป..."
summary = model.summarize_text(text, max_length=100)
print(summary)
```

### **API Client Usage**

```python
import requests

# Chat completion
response = requests.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "thai-model",
        "messages": [
            {"role": "user", "content": "สวัสดี"}
        ],
        "max_tokens": 100
    }
)
print(response.json())

# Text summarization
response = requests.post(
    "http://localhost:8001/v1/summarize",
    json={
        "text": "ข้อความที่ต้องการสรุป...",
        "max_tokens": 50
    }
)
print(response.json())
```

### **Training a Custom Model**

```python
from thai_model.training import ThaiModelTrainer
from thai_model.core.config import TrainingConfig

# Load training configuration
config = TrainingConfig.from_yaml("config/training_config.yaml")

# Initialize trainer
trainer = ThaiModelTrainer(config)

# Train model
trainer.train()

# Evaluate model
results = trainer.evaluate()
print(results)
```

## ⚙️ Configuration

### **Model Configuration**

Edit `config/model_config.yaml`:

```yaml
model:
  model_name: "Qwen/Qwen2.5-1.5B-Instruct"
  adapter_path: "./models/checkpoints/qwen_thai_lora"
  device: "auto"
  torch_dtype: "float16"
  max_new_tokens: 512
  temperature: 0.7

api:
  host: "0.0.0.0"
  port: 8001
  workers: 1
```

### **Training Configuration**

Edit `config/training_config.yaml`:

```yaml
model:
  base_model: "Qwen/Qwen2.5-1.5B-Instruct"
  output_dir: "./models/checkpoints"

lora:
  r: 16
  alpha: 32
  dropout: 0.05

training:
  num_train_epochs: 3
  learning_rate: 2.0e-4
  per_device_train_batch_size: 1
```

## 📚 API Documentation

### **Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/v1/models` | List available models |
| POST | `/v1/chat/completions` | OpenAI-compatible chat |
| POST | `/v1/summarize` | Thai text summarization |
| POST | `/v1/generate` | General text generation |

### **Chat Completions**

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
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

### **Text Summarization**

```bash
curl -X POST http://localhost:8001/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ข้อความยาว ๆ ที่ต้องการสรุป...",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

For complete API documentation, visit `/docs` when the server is running.

## 🐳 Deployment

### **Docker Deployment**

```bash
# Build image
cd deployment/docker
docker build -f Dockerfile.cpu -t thai-model-api .

# Run container
docker run -d -p 8001:8001 \
  -v ./models:/app/models:ro \
  -v ./config:/app/config:ro \
  thai-model-api

# Or use docker-compose
docker-compose up -d
```

### **Kubernetes Deployment**

```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/
```

### **Production Setup**

For production deployment with monitoring:

```bash
# Start full production stack
cd deployment/docker
docker-compose -f docker-compose.prod.yml up -d
```

This includes:
- API server with load balancing
- Nginx reverse proxy
- Prometheus metrics collection
- Grafana dashboards
- Redis caching

## 🛠️ Development

### **Setting Up Development Environment**

```bash
# Clone repository
git clone https://github.com/username/thai-language-model.git
cd thai-language-model

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### **Running Tests**

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest thai_model/tests/test_api.py  # API tests only

# Run with coverage
pytest --cov=thai_model --cov-report=html
```

### **Code Formatting**

```bash
# Format code
black thai_model/ scripts/
isort thai_model/ scripts/

# Type checking
mypy thai_model/
```

### **Building Documentation**

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
cd docs/
make html
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### **Development Workflow**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

### **Reporting Issues**

Please use the [GitHub Issues](https://github.com/username/thai-language-model/issues) page to report bugs or request features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Qwen Team** for the base model
- **Hugging Face** for the transformers library
- **Thai NLP Community** for datasets and resources
- **Contributors** who have helped improve this project

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/username/thai-language-model/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/thai-language-model/discussions)

---

**Built with ❤️ for the Thai language AI community**
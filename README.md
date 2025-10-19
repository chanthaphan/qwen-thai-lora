# 🇹🇭 Thai Language Model Project

A comprehensive Python project for fine-tuning and deploying Thai language models using state-of-the-art techniques including LoRA (Low-Rank Adaptation) and modern hosting solutions.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd project
./setup.sh

# Train Thai model
./manage.sh train

# Start web interface
./manage.sh host-gui

# Or start API server
./manage.sh host-api
```

## 📁 Project Structure

```
project/
├── 📚 src/                     # Source code
│   ├── 🧠 training/            # Model training scripts
│   │   ├── finetune_thai_model.py
│   │   └── merge_lora_model.py
│   ├── 🌐 hosting/             # Model hosting servers
│   │   ├── fastapi_server.py
│   │   └── host_thai_model.py
│   ├── 🖥️ interfaces/          # User interfaces
│   │   ├── gradio_gui.py
│   │   ├── ollama_chat.py
│   │   └── vllm_chat.py
│   ├── 🧪 testing/             # Test scripts
│   │   ├── test_model.py
│   │   └── test_simple.py
│   └── 🔧 utils/               # Utility functions
├── 🏗️ models/                  # Trained models
│   └── qwen_thai_lora/         # Thai LoRA model
├── 📋 config/                  # Configuration files
│   └── requirements.txt
├── 🐳 deployment/              # Deployment files
│   ├── Dockerfile
│   └── docker-compose.yml
├── 📖 docs/                    # Documentation
├── 🛠️ scripts/                 # Utility scripts
├── 📊 logs/                    # Training logs
├── 💾 data/                    # Dataset cache
├── manage.sh                   # 🎯 Project manager
└── setup.sh                   # ⚡ Quick setup
```

## 🎯 Project Manager

Use the `./manage.sh` script for all common tasks:

```bash
# Setup and environment
./manage.sh setup          # Setup project environment
./manage.sh status         # Show project status
./manage.sh clean          # Clean temporary files

# Training and testing
./manage.sh train          # Train Thai model
./manage.sh test           # Run comprehensive tests
./manage.sh test-simple    # Run quick model test
./manage.sh merge-model    # Merge LoRA with base model

# Hosting and interfaces
./manage.sh host-gui       # Start Gradio web interface
./manage.sh host-api       # Start FastAPI server
./manage.sh chat-ollama    # Start Ollama chat app
./manage.sh chat-vllm      # Start vLLM chat app

# Docker deployment
./manage.sh docker-build   # Build Docker image
./manage.sh docker-run     # Run Docker container

./manage.sh help           # Show all commands
```

## 🧠 Features

### 🎓 Training Capabilities
- **LoRA Fine-tuning**: Parameter-efficient training with PEFT library
- **Thai Dataset**: pythainlp/thaisum with 350k+ Thai news articles
- **Modern Framework**: Uses TRL SFTTrainer with transformers 4.35+
- **Evaluation Metrics**: ROUGE score evaluation for summarization quality
- **GPU Optimization**: Mixed precision training with accelerate

### 🌐 Hosting Options
- **FastAPI Server**: Production-ready API with OpenAI-compatible endpoints
- **Gradio Web UI**: User-friendly web interface for Thai summarization
- **Docker Support**: Containerized deployment with GPU support
- **vLLM Integration**: High-performance inference server option
- **Ollama Chat**: Interactive chat interface for Ollama models

### 🔧 Technical Stack
- **Base Model**: Qwen2.5-1.5B-Instruct
- **Fine-tuning**: PEFT LoRA (rank 16, alpha 32)
- **Framework**: PyTorch + Transformers + TRL
- **Language Processing**: pythainlp for Thai text handling
- **APIs**: FastAPI with automatic OpenAPI documentation
- **Frontend**: Gradio for web interfaces

## 📊 Training Details

The model is fine-tuned on Thai news summarization using:

- **Dataset**: pythainlp/thaisum (Thai news articles with summaries)
- **Architecture**: Qwen2.5-1.5B-Instruct with LoRA adapters
- **Training**: 3 epochs with gradient accumulation
- **Optimization**: AdamW optimizer with learning rate scheduling
- **Evaluation**: ROUGE-1, ROUGE-2, ROUGE-L metrics

### 🎯 Performance
- **Model Size**: ~1.5B parameters (base) + ~8M (LoRA)
- **Training Time**: ~2-3 hours on RTX 4090
- **Memory Usage**: ~6-8GB VRAM during training
- **Inference Speed**: ~10-15 tokens/second

## 🚀 Usage Examples

### Python API
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load model
base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
model = PeftModel.from_pretrained(base_model, "models/qwen_thai_lora")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")

# Generate summary
prompt = "สรุปข่าวนี้: [Thai news article]"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_length=200)
summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### FastAPI Server
```bash
# Start server
./manage.sh host-api

# Use API
curl -X POST "http://localhost:8001/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-model",
    "messages": [{"role": "user", "content": "สรุปข่าวนี้: ..."}]
  }'
```

### Web Interface
```bash
# Start Gradio interface
./manage.sh host-gui

# Open browser to http://localhost:7860
```

## 🛠️ Development

### Environment Setup
```bash
# Manual setup
python3 -m venv llm-env
source llm-env/bin/activate
pip install -r config/requirements.txt

# Or use quick setup
./setup.sh
```

### Adding New Features
1. **Training**: Add scripts to `src/training/`
2. **Hosting**: Add servers to `src/hosting/`
3. **Interfaces**: Add UIs to `src/interfaces/`
4. **Tests**: Add tests to `src/testing/`
5. **Utils**: Add utilities to `src/utils/`

### Testing
```bash
# Quick test
./manage.sh test-simple

# Full test suite
./manage.sh test

# Manual testing
source llm-env/bin/activate
python src/testing/test_model.py
```

## 🐳 Docker Deployment

```bash
# Build and run
./manage.sh docker-build
./manage.sh docker-run

# Or use docker-compose
cd deployment
docker-compose up -d
```

## 📈 Performance Tuning

### Training Optimization
- Adjust LoRA rank/alpha in training script
- Modify batch size based on GPU memory
- Experiment with different learning rates
- Use gradient checkpointing for larger models

### Inference Optimization
- Use model quantization for smaller memory footprint
- Implement response caching for common queries
- Deploy on multiple GPUs for higher throughput
- Use vLLM for production-scale inference

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test: `./manage.sh test`
4. Commit changes: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature-name`
6. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Qwen Team**: For the excellent base model
- **Hugging Face**: For transformers and PEFT libraries
- **Thai NLP Community**: For pythainlp and Thai datasets
- **Meta**: For LoRA technique and research

## 📞 Support

- 📧 Issues: Use GitHub Issues for bug reports
- 💬 Discussions: Use GitHub Discussions for questions
- 📚 Documentation: Check `docs/` folder for detailed guides
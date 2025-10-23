# 📚 Thai Model Project Documentation

Welcome to the comprehensive documentation for the Thai Language Model project! This directory contains all technical documentation, implementation guides, and development resources.

## 🎯 **Quick Navigation**

### **🚀 Getting Started**
- [`../README.md`](../README.md) - Project overview and main features
- [`../QUICK_START.md`](../QUICK_START.md) - 5-minute quick start guide
- [`HOSTING_GUIDE.md`](HOSTING_GUIDE.md) - Production deployment guide

### **🤖 AI Integration Guides**
- [`OPENAI_INTEGRATION.md`](OPENAI_INTEGRATION.md) - OpenAI API integration
- [`OPENAI_SETUP_GUIDE.md`](OPENAI_SETUP_GUIDE.md) - OpenAI configuration
- [`OPENAI_IMPLEMENTATION_SUMMARY.md`](OPENAI_IMPLEMENTATION_SUMMARY.md) - Implementation details
- [`OPENAI_WEB_INTEGRATION.md`](OPENAI_WEB_INTEGRATION.md) - Web interface integration

### **💾 Database & Persistence**
- [`POSTGRESQL_INTEGRATION.md`](POSTGRESQL_INTEGRATION.md) - PostgreSQL setup and integration
- [`POSTGRES_IMPLEMENTATION_SUMMARY.md`](POSTGRES_IMPLEMENTATION_SUMMARY.md) - Database implementation
- [`POSTGRES_SUCCESS.md`](POSTGRES_SUCCESS.md) - Successful implementation summary

### **🛠️ Implementation & Development**
- [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) - Complete project implementation
- [`CHAT_FORMAT_FIX.md`](CHAT_FORMAT_FIX.md) - Gradio format compatibility fixes
- [`CHAT_INTERFACE_TEST_SUCCESS.md`](CHAT_INTERFACE_TEST_SUCCESS.md) - Interface testing results
- [`TRAINING_SUMMARY.md`](TRAINING_SUMMARY.md) - Model training documentation

### **⚙️ System Management**
- [`VLLM_MANAGEMENT.md`](VLLM_MANAGEMENT.md) - vLLM server management
- [`MANAGE_RESTRUCTURE.md`](MANAGE_RESTRUCTURE.md) - Project restructuring guide

## 🏗️ **Project Architecture**

This Thai Language Model project features:
- **Multi-Backend AI Support**: vLLM (Thai model), Ollama (local), OpenAI (cloud)
- **Enterprise Database**: PostgreSQL-backed persistent chat history
- **Modern Web Interface**: Gradio-based UI with session management
- **Production Ready**: Docker containers, monitoring, deployment scripts

## 📋 Requirements

### System Requirements
- Python 3.8+
- CUDA-compatible GPU (recommended for training)
- 8GB+ GPU memory (for training)
- 16GB+ RAM

### Dependencies
```bash
pip install torch transformers peft datasets trl accelerate bitsandbytes
```

Or install from requirements in the virtual environment:
```bash
python -m venv llm-env
source llm-env/bin/activate  # On Linux/Mac
# llm-env\Scripts\activate    # On Windows
pip install -r requirements.txt  # If requirements.txt exists
```

## 🛠️ Setup

1. **Clone the repository:**
```bash
git clone https://github.com/chanthaphan/qwen-thai-lora.git
cd qwen-thai-lora
```

2. **Set up Python environment:**
```bash
python -m venv llm-env
source llm-env/bin/activate
pip install torch transformers peft datasets trl accelerate bitsandbytes
```

3. **Verify GPU access (optional but recommended):**
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## 🔧 Usage

### Fine-tuning the Model

Run the main fine-tuning script:
```bash
python finetune_quen3_lora.py
```

This will:
- Load the Qwen2.5-1.5B-Instruct base model
- Apply LoRA adapters for efficient fine-tuning
- Train on Thai text summarization data
- Save the fine-tuned model to `./qwen_thai_lora/`

### Testing the Fine-tuned Model

After training, test the model:
```bash
python test_thai_model.py
```

This script will:
- Load your fine-tuned model
- Generate Thai summaries for sample news articles
- Display original text alongside generated summaries

### Chat Applications

The project includes several chat applications for comparison:

**Ollama Integration:**
```bash
export OLLAMA_HOST=localhost:11434
python chat_app.py                    # Interactive chat
python chat_app.py "สวัสดี"          # Direct prompt
python chat_gui.py                    # Web GUI
```

**vLLM Integration:**
```bash
python chat_app_vllm.py
```

## 📁 Project Structure

```
qwen-thai-lora/
├── finetune_quen3_lora.py      # Main fine-tuning script
├── test_thai_model.py          # Model testing and evaluation
├── chat_app.py                 # Ollama chat application
├── chat_app_vllm.py           # vLLM chat application  
├── chat_gui.py                # Gradio web interface
├── chat_ollama.py             # Ollama integration utilities
├── test_streaming.py          # Streaming response testing
├── launch_gui.sh              # GUI launcher script
├── .gitignore                 # Git ignore rules
├── TRAINING_SUMMARY.md        # Detailed training documentation
└── README.md                  # This file
```

## ⚙️ Configuration

### Model Parameters
- **Base Model**: Qwen2.5-1.5B-Instruct
- **LoRA Rank**: 16
- **LoRA Alpha**: 32
- **Target Modules**: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
- **Dropout**: 0.1

### Training Parameters
- **Batch Size**: 4
- **Learning Rate**: 2e-4
- **Training Steps**: 100 (configurable)
- **Max Sequence Length**: 512
- **Optimizer**: AdamW
- **Scheduler**: Linear with warmup

## 🎯 Model Performance

The fine-tuned model specializes in:
- Thai news article summarization
- Thai language understanding and generation
- Maintaining context in Thai text processing
- Generating coherent Thai summaries

See `TRAINING_SUMMARY.md` for detailed training metrics and evaluation results.

## 📊 Dataset

The model is trained on Thai text summarization datasets, focusing on:
- Thai news articles and their summaries
- Various domains including politics, sports, entertainment, and technology
- High-quality Thai language pairs for supervised fine-tuning

## 🔍 Troubleshooting

### Common Issues

**CUDA Out of Memory:**
- Reduce batch size in training script
- Enable gradient checkpointing (already enabled)
- Use smaller sequence lengths

**Model Loading Issues:**
- Ensure sufficient disk space for model downloads
- Check internet connection for Hugging Face downloads
- Verify model path after training completion

**Thai Text Encoding:**
- Ensure UTF-8 encoding for all Thai text files
- Check terminal/IDE supports Thai character display

### Performance Tips

- Use GPU for training (CPU training will be very slow)
- Monitor GPU memory usage during training
- Adjust batch size based on available GPU memory
- Use mixed precision training (fp16) for memory efficiency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source. Please check individual model licenses:
- Qwen2.5 model: See Hugging Face model page for license details
- Training code: MIT License (or specify your preferred license)

## 🙏 Acknowledgments

- **Qwen Team** for the excellent Qwen2.5 base model
- **Hugging Face** for the transformers and PEFT libraries
- **Microsoft** for the LoRA implementation
- **Thai NLP Community** for Thai language resources and datasets

## 📞 Support

If you encounter issues or have questions:
1. Check the troubleshooting section above
2. Review `TRAINING_SUMMARY.md` for detailed documentation
3. Open an issue on GitHub
4. Check Hugging Face documentation for model-specific questions

---

**Happy Fine-tuning! 🇹🇭🤖**
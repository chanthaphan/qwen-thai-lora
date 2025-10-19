# 🚀 Thai Model Hosting Guide

This guide shows you how to host your fine-tuned Thai model using different methods, from simple local hosting to production-ready deployments.

## 📋 Prerequisites

Before hosting, ensure you have:
- ✅ Trained Thai model in `./qwen_thai_lora/`
- ✅ Virtual environment with required packages
- ✅ Python 3.8+ installed

## 🎯 Hosting Options

### **Option 1: vLLM Server (Recommended for API)**

**Best for**: Production API, high performance, OpenAI-compatible endpoints

```bash
# Start vLLM server with your Thai model
python host_thai_model.py
```

**Features**:
- 🚀 High performance inference
- 📡 OpenAI-compatible API
- 🔄 Automatic batching
- 💾 Memory efficient

**Access**:
- API: `http://localhost:8000/v1/chat/completions`
- Model name: `thai-qwen-lora`

**Test with**:
```bash
export VLLM_HOST=localhost:8000
python chat_app_vllm.py --model thai-qwen-lora "สรุปข่าวนี้"
```

---

### **Option 2: Gradio Web Interface (Recommended for GUI)**

**Best for**: User-friendly interface, demonstrations, testing

```bash
# Start web interface
python thai_model_gui.py
```

**Features**:
- 🖥️ Beautiful web interface
- 📝 Thai text summarization
- 💬 Chat interface
- ⚙️ Adjustable settings

**Access**: http://localhost:7862

---

### **Option 3: FastAPI Server (Recommended for Production)**

**Best for**: Custom APIs, production deployments, integration

```bash
# Install FastAPI dependencies
pip install fastapi uvicorn

# Start FastAPI server
python thai_model_api.py
```

**Features**:
- 🔧 Custom endpoints
- 📚 Automatic API docs
- 🔍 Health checks
- 📊 Usage statistics

**Access**:
- API: http://localhost:8001
- Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

**Endpoints**:
```bash
# Chat completion (OpenAI-compatible)
POST /v1/chat/completions

# Thai summarization
POST /v1/summarize

# List models
GET /v1/models
```

---

### **Option 4: Docker Container (Production Ready)**

**Best for**: Production deployment, scalability, cloud hosting

```bash
# Build Docker image
docker build -t thai-model-api .

# Run container
docker run -p 8001:8001 --gpus all thai-model-api

# Or use docker-compose
docker-compose up
```

**Features**:
- 🐳 Containerized deployment
- 🔄 Auto-restart
- 📊 Health monitoring
- 🌐 Cloud-ready

---

## 🔧 Testing Your Hosted Model

### **1. Test with curl**
```bash
# Test summarization endpoint
curl -X POST "http://localhost:8001/v1/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "นักวิทยาศาสตร์ได้พัฒนาเทคโนโลยีปัญญาประดิษฐ์ใหม่ที่สามารถช่วยในการวินิจฉัยโรคได้อย่างแม่นยำ",
    "max_tokens": 100,
    "temperature": 0.7
  }'

# Test chat endpoint (OpenAI-compatible)
curl -X POST "http://localhost:8001/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-qwen-lora",
    "messages": [
      {"role": "user", "content": "สรุปข่าวเกี่ยวกับเทคโนโลยี AI ใหม่"}
    ],
    "max_tokens": 150
  }'
```

### **2. Test with Python**
```python
import requests

# Test summarization
response = requests.post("http://localhost:8001/v1/summarize", 
    json={
        "text": "ข่าวภาษาไทยที่ต้องการสรุป...",
        "max_tokens": 100
    })
print(response.json())

# Test with existing chat app
# python chat_app_vllm.py --url http://localhost:8001 --model thai-qwen-lora
```

### **3. Test with existing apps**
```bash
# Use with vLLM chat app
export VLLM_HOST=localhost:8001
python chat_app_vllm.py --model thai-qwen-lora

# Direct testing
python test_thai_model.py
```

---

## 🌐 Cloud Deployment Options

### **1. Google Cloud Run**
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT-ID/thai-model
gcloud run deploy --image gcr.io/PROJECT-ID/thai-model --platform managed
```

### **2. AWS ECS/Fargate**
```bash
# Push to ECR and deploy
aws ecr get-login-password | docker login --username AWS --password-stdin
docker tag thai-model-api:latest AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/thai-model
docker push AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/thai-model
```

### **3. Hugging Face Spaces**
```python
# Create a Gradio app for Hugging Face Spaces
# Upload thai_model_gui.py to your Space
# Add requirements.txt with dependencies
```

---

## ⚡ Performance Optimization

### **GPU Optimization**
```python
# Enable GPU acceleration
export CUDA_VISIBLE_DEVICES=0

# Use mixed precision
--dtype float16

# Optimize batch size
--max-model-len 2048
```

### **Memory Optimization**
```python
# Use quantization
--quantization awq  # or --load-in-8bit

# Reduce model length
--max-model-len 1024
```

---

## 🔍 Monitoring and Logging

### **Health Checks**
```bash
# Check if server is running
curl http://localhost:8001/health

# Monitor GPU usage
nvidia-smi -l 1
```

### **Logging**
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.INFO)
```

---

## 🚨 Troubleshooting

### **Common Issues**

**Model not loading:**
```bash
# Check model path
ls -la ./qwen_thai_lora/

# Verify dependencies
pip install -r requirements.txt
```

**Out of memory:**
```bash
# Reduce batch size or use quantization
--dtype float16 --max-model-len 1024
```

**Port conflicts:**
```bash
# Use different port
uvicorn thai_model_api:app --port 8002
```

---

## 📊 Performance Comparison

| Method | Setup Difficulty | Performance | Features | Best For |
|--------|------------------|-------------|----------|----------|
| vLLM | Medium | ⭐⭐⭐⭐⭐ | API, Batching | Production API |
| Gradio | Easy | ⭐⭐⭐ | GUI, Interactive | Demos, Testing |
| FastAPI | Medium | ⭐⭐⭐⭐ | Custom API | Custom Integration |
| Docker | Hard | ⭐⭐⭐⭐⭐ | Scalable | Cloud Deployment |

---

## 🎉 Next Steps

1. **Choose your hosting method** based on your needs
2. **Test the deployment** with sample Thai text
3. **Monitor performance** and optimize as needed
4. **Scale up** for production if required

Your Thai model is now ready to serve real users! 🇹🇭🚀
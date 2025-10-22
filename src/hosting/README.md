# Hosting Module Documentation

## Overview
The Hosting Module provides production-ready deployment options for your Thai Language Model. It includes FastAPI server setup, production configurations, monitoring, and various deployment strategies.

## 📁 Module Structure

```
src/hosting/
├── __init__.py              # Module initialization
├── fastapi_server.py        # Main FastAPI server implementation
├── host_model.py            # Host model management script  
├── test_api_client.py       # API client testing script
└── setup_production.py     # Production deployment generator
```

## 🚀 Hosting Options

### 1. Development Server
Quick startup for development and testing:
```bash
# Using management script
./manage.sh host-api

# Using startup script
./start_api.sh

# Direct execution
./llm-env/bin/python src/hosting/fastapi_server.py
```

### 2. Production Deployment
Generate production configuration files:
```bash
./llm-env/bin/python src/hosting/setup_production.py
```

This creates:
- `thai-model-api.service` - Systemd service file
- `thai-model-api.nginx` - Nginx reverse proxy configuration
- `docker-compose.prod.yml` - Docker Compose setup
- `monitoring/prometheus.yml` - Monitoring configuration
- `start_api.sh` - Development startup script

## 📡 API Endpoints

### Server Information
- **GET /** - Server information and available endpoints
- **GET /health** - Health check and model status
- **GET /v1/models** - List available models (OpenAI-compatible)

### Text Processing
- **POST /v1/summarize** - Thai text summarization (custom endpoint)
- **POST /v1/chat/completions** - OpenAI-compatible chat completions

### API Documentation
- **GET /docs** - Interactive API documentation (Swagger UI)
- **GET /redoc** - Alternative API documentation

## 🔧 Configuration

### Model Configuration
```python
# In fastapi_server.py
base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
lora_model_path = "./models/qwen_thai_lora"
```

### Server Configuration
```python
# Server settings
host = "0.0.0.0"          # Listen on all interfaces
port = 8001               # API server port
reload = False            # Disable auto-reload in production
access_log = True         # Enable access logging
```

### Generation Parameters
```python
# Text generation settings
max_new_tokens = 150      # Maximum tokens to generate
temperature = 0.7         # Sampling temperature (0.0-2.0)
top_p = 0.9              # Nucleus sampling parameter
no_repeat_ngram_size = 3  # Prevent repetition
```

## 📝 API Usage Examples

### 1. Thai Text Summarization
```bash
curl -X POST http://localhost:8001/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ข้อความที่ต้องการสรุปเป็นภาษาไทย...",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "summary": "สรุปข้อความเป็นภาษาไทย",
  "model": "thai-qwen-lora",
  "usage": {
    "input_tokens": 45,
    "output_tokens": 32,
    "total_tokens": 77
  }
}
```

### 2. OpenAI-Compatible Chat
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-qwen-lora",
    "messages": [
      {"role": "user", "content": "สรุปประโยชน์ของการออกกำลังกาย"}
    ],
    "max_tokens": 80,
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "thai-qwen-lora",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "การออกกำลังกายช่วยให้ร่างกายแข็งแรง..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 25,
    "total_tokens": 40
  }
}
```

### 3. Python Client Integration
```python
import requests

# Initialize client
api_url = "http://localhost:8001"

# Test summarization
response = requests.post(f"{api_url}/v1/summarize", json={
    "text": "ข้อความภาษาไทยที่ต้องการสรุป",
    "max_tokens": 100
})
summary = response.json()["summary"]

# Test chat completion  
response = requests.post(f"{api_url}/v1/chat/completions", json={
    "model": "thai-qwen-lora",
    "messages": [{"role": "user", "content": "คำถาม"}],
    "max_tokens": 80
})
answer = response.json()["choices"][0]["message"]["content"]
```

## 🏭 Production Deployment

### Option 1: Systemd Service
```bash
# Install service
sudo cp thai-model-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable thai-model-api
sudo systemctl start thai-model-api

# Check status
sudo systemctl status thai-model-api
sudo journalctl -u thai-model-api -f
```

### Option 2: Docker Deployment
```bash
# Build and run
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale service
docker-compose -f docker-compose.prod.yml up -d --scale thai-model-api=3
```

### Option 3: Nginx Reverse Proxy
```bash
# Install nginx configuration
sudo cp thai-model-api.nginx /etc/nginx/sites-available/thai-model-api
sudo ln -s /etc/nginx/sites-available/thai-model-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Performance Characteristics

### Model Loading
- **Cold start**: ~10-15 seconds (first request)
- **Warm requests**: <1 second (subsequent requests)
- **Memory usage**: ~4GB GPU memory (float16)
- **Model size**: 3GB base + 17MB LoRA adapter

### API Performance
Based on recent testing:
- **Summarization**: 2-11 seconds per request
- **Chat completion**: 2-3 seconds per request
- **Throughput**: 1-2 requests per second (single GPU)
- **Concurrent requests**: Limited by GPU memory

### Scaling Recommendations
- **Single GPU**: 1-2 concurrent requests
- **Multiple GPUs**: Use model parallelism or multiple instances
- **CPU inference**: Possible but much slower (30-60s per request)
- **Load balancing**: Use nginx upstream for multiple instances

## 🔍 Monitoring & Debugging

### Health Monitoring
```bash
# Check server health
curl http://localhost:8001/health

# Check if model is loaded
curl http://localhost:8001/health | grep model_loaded
```

### Log Analysis
```bash
# View server logs (systemd)
sudo journalctl -u thai-model-api -f

# View startup script logs
tail -f api_test.log

# Check for errors
grep ERROR api_test.log
```

### Performance Monitoring
```bash
# Check GPU usage
nvidia-smi

# Monitor API metrics (if Prometheus enabled)
curl http://localhost:8001/metrics

# Test API response times
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8001/health
```

## 🛠 Troubleshooting

### Common Issues

#### Model Not Found
```
❌ Thai model not found at ./models/qwen_thai_lora
```
**Solution**: Ensure model training completed successfully
```bash
ls -la models/qwen_thai_lora/
# Should contain: adapter_config.json, adapter_model.safetensors, tokenizer files
```

#### Port Already in Use
```
OSError: [Errno 98] Address already in use
```
**Solution**: Kill existing process or use different port
```bash
lsof -i :8001
kill -9 <PID>
```

#### GPU Memory Issues
```
RuntimeError: CUDA out of memory
```
**Solutions**:
- Reduce batch size or max_tokens
- Use CPU inference: `device_map="cpu"`
- Close other GPU processes

#### Model Loading Timeout
```
HTTPException: Error loading model: timeout
```
**Solutions**:
- Increase server timeout settings
- Pre-load model on startup
- Use faster storage (SSD)

### Performance Optimization

#### Model Optimization
```python
# Use int8 quantization for memory saving
import torch
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)
```

#### Server Optimization
```python
# Enable multiple workers (CPU-bound tasks)
uvicorn.run(app, host="0.0.0.0", port=8001, workers=2)

# Use async processing for concurrent requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
```

## 🔒 Security Considerations

### API Security
- **Rate limiting**: Implemented in nginx configuration
- **CORS**: Configured for cross-origin requests
- **Input validation**: Automatic via Pydantic models
- **Request size limits**: Set max content length

### Production Security
```bash
# Firewall configuration
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8001  # Don't expose FastAPI directly

# SSL/TLS encryption
sudo certbot --nginx -d your-domain.com

# Regular security updates
sudo apt update && sudo apt upgrade
```

## 🎯 Integration Examples

### Frontend Integration (JavaScript)
```javascript
// Fetch API
const response = await fetch('http://localhost:8001/v1/summarize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: 'ข้อความที่ต้องการสรุป',
    max_tokens: 100
  })
});
const result = await response.json();
console.log(result.summary);
```

### Backend Integration (Python)
```python
# Using OpenAI client library
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="not-required-for-local"
)

response = client.chat.completions.create(
    model="thai-qwen-lora",
    messages=[{"role": "user", "content": "คำถาม"}]
)
print(response.choices[0].message.content)
```

## 🎉 Success Criteria

Your hosting module is working correctly when:
- ✅ All API endpoints respond successfully
- ✅ Thai model loads and generates coherent text
- ✅ Response times are acceptable (< 30 seconds)
- ✅ Health checks pass consistently
- ✅ Server runs stably under load
- ✅ Error handling works properly

Ready for production when:
- ✅ SSL/TLS encryption enabled
- ✅ Rate limiting configured
- ✅ Monitoring and logging set up
- ✅ Backup and recovery procedures tested
- ✅ Security hardening completed
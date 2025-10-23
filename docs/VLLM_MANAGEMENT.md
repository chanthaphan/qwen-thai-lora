# vLLM Model Management Guide

## 🎯 **Current Model Configuration**

Your vLLM setup is correctly configured with:

- **Base Model**: `Qwen/Qwen2.5-1.5B-Instruct` ✅
- **Thai Model**: `models/qwen_thai_merged` (2.9GB) ✅
- **LoRA Adapter**: `models/qwen_thai_lora` (163MB) ✅
- **Server Status**: Running on port 8000 ✅

## 🚀 **Quick Commands**

### **Basic Management:**
```bash
# Check status
./manage.sh vllm status

# Start server
./manage.sh vllm start

# Stop server  
./manage.sh vllm stop

# Restart server
./manage.sh vllm restart

# Test functionality
./manage.sh vllm test
```

### **Alternative Commands:**
```bash
# Direct script access
./scripts/manage_vllm.sh status
./scripts/manage_vllm.sh start
./scripts/manage_vllm.sh test

# Traditional manage.sh commands
./manage.sh host-vllm    # Start vLLM (traditional way)
```

## 📊 **Model Information**

### **Model Hierarchy:**
1. **Thai Merged Model** (Recommended) ⭐
   - Path: `models/qwen_thai_merged`
   - Size: 2.9GB
   - Contains: Base model + Thai LoRA merged
   - Best for: Production use with Thai capabilities

2. **Base Model** (Fallback)
   - Path: `Qwen/Qwen2.5-1.5B-Instruct`
   - Size: Downloaded from HuggingFace
   - Contains: Original Qwen2.5-1.5B model
   - Best for: Testing, no Thai specialization

3. **LoRA Adapter** (Development)
   - Path: `models/qwen_thai_lora`
   - Size: 163MB
   - Contains: Thai fine-tuning weights
   - Best for: Development, needs merging

## ⚙️ **Advanced Configuration**

### **Performance Tuning:**
```bash
# Current vLLM parameters:
--model "models/qwen_thai_merged"
--host 0.0.0.0
--port 8000
--served-model-name thai-model
--max-model-len 4096
--gpu-memory-utilization 0.8
--dtype float16
```

### **Memory Optimization:**
- **GPU Memory**: 80% utilization (--gpu-memory-utilization 0.8)
- **Data Type**: Float16 for efficiency (--dtype float16)
- **Max Length**: 4096 tokens (--max-model-len 4096)

### **Custom Configuration:**
```bash
# Edit vLLM parameters
./manage.sh vllm config

# View detailed logs
./manage.sh vllm logs

# Manual server start with custom options
llm-env/bin/python -m vllm.entrypoints.openai.api_server \
    --model "models/qwen_thai_merged" \
    --host 0.0.0.0 \
    --port 8000 \
    --served-model-name thai-model \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.9
```

## 🧪 **API Testing**

### **Health Check:**
```bash
curl http://localhost:8000/health
```

### **List Models:**
```bash
curl http://localhost:8000/v1/models
```

### **Chat Completion:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-model",
    "messages": [{"role": "user", "content": "สวัสดี"}],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### **Streaming Response:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-model",
    "messages": [{"role": "user", "content": "เล่าเรื่องสั้น"}],
    "max_tokens": 200,
    "stream": true
  }'
```

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. Server Won't Start:**
```bash
# Check if port is in use
lsof -i :8000

# Kill existing processes
pkill -f vllm

# Check logs
./manage.sh vllm logs
```

#### **2. Out of Memory:**
```bash
# Reduce GPU memory utilization
--gpu-memory-utilization 0.6

# Use smaller model
--model "Qwen/Qwen2.5-1.5B-Instruct"
```

#### **3. Slow Performance:**
```bash
# Enable tensor parallelism (multi-GPU)
--tensor-parallel-size 2

# Reduce max length
--max-model-len 2048
```

## 📈 **Model Switching**

### **To Use Base Model:**
```bash
# Temporarily rename merged model
mv models/qwen_thai_merged models/qwen_thai_merged.backup
./manage.sh vllm restart
```

### **To Use Thai Model:**
```bash
# Restore merged model
mv models/qwen_thai_merged.backup models/qwen_thai_merged
./manage.sh vllm restart
```

### **To Create New Merged Model:**
```bash
# Merge LoRA with base model
./manage.sh merge-model

# This will create a new merged model
```

## 🌐 **Integration**

### **With Chat Applications:**
```bash
# Use vLLM with chat interfaces
./manage.sh chat-vllm     # vLLM chat client
./manage.sh chat-web      # Web interface with vLLM backend
```

### **With API Clients:**
- **OpenAI Python SDK**: Compatible endpoint
- **curl**: Direct HTTP API calls  
- **Postman**: API testing and development
- **Gradio**: Web interface integration

## 📊 **Monitoring**

### **Real-time Monitoring:**
```bash
# Watch server logs
tail -f logs/vllm_server.log

# Monitor GPU usage
nvidia-smi -l 1

# Check server status
watch -n 5 './manage.sh vllm status'
```

### **Performance Metrics:**
- **Latency**: Response time per request
- **Throughput**: Requests per second
- **GPU Utilization**: Memory and compute usage
- **Queue Depth**: Pending requests

---

## 🎉 **Summary**

Your vLLM setup is **optimally configured** with:

✅ **Correct Model**: Qwen2.5-1.5B-Instruct (not 4B)  
✅ **Thai Capabilities**: Merged model with Thai LoRA  
✅ **Production Ready**: Advanced management tools  
✅ **API Compatible**: OpenAI-style endpoints  
✅ **High Performance**: GPU-optimized inference  

Use `./manage.sh vllm status` to check your setup anytime! 🚀
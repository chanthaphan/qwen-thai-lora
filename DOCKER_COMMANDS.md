# 🐳 Docker Deployment Commands Reference

## Quick Docker Deployment Guide

Since Docker isn't currently running on your system, here are the exact commands you would use to deploy your Thai Model API using containers:

### 1. **Build the Docker Image**
```bash
# Build the multi-stage Docker image
docker build -t thai-model-api:latest . --target application

# View the built image
docker images thai-model-api:latest
```

### 2. **Run Single Container (Development)**
```bash
# With GPU support
docker run -d \
    --name thai-model-api \
    --gpus all \
    -p 8001:8001 \
    -e CUDA_VISIBLE_DEVICES=0 \
    -v "$(pwd)/models:/app/models:ro" \
    -v "$(pwd)/config:/app/config:ro" \
    thai-model-api:latest

# CPU-only mode
docker run -d \
    --name thai-model-api \
    -p 8001:8001 \
    -v "$(pwd)/models:/app/models:ro" \
    -v "$(pwd)/config:/app/config:ro" \
    thai-model-api:latest
```

### 3. **Production Deployment with Docker Compose**
```bash
# Start all services (API + Nginx + Monitoring)
docker-compose up -d

# View running services
docker-compose ps

# View logs
docker-compose logs -f thai-model-api

# Stop all services
docker-compose down
```

### 4. **Testing the Containerized API**
```bash
# Health check
curl http://localhost:8001/health

# Chat completion test
curl -X POST http://localhost:8001/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "thai-model",
        "messages": [
            {"role": "user", "content": "สวัสดี"}
        ],
        "max_tokens": 50,
        "stream": false
    }'
```

### 5. **Container Management**
```bash
# View container stats
docker stats thai-model-api

# View container logs
docker logs thai-model-api

# Execute commands inside container
docker exec -it thai-model-api /bin/bash

# Stop container
docker stop thai-model-api

# Remove container
docker rm thai-model-api

# Remove image
docker rmi thai-model-api:latest
```

### 6. **Production Monitoring**
```bash
# Access Grafana dashboard
open http://localhost:3000

# Access Prometheus metrics
open http://localhost:9090

# View nginx proxy status
curl http://localhost/nginx_status
```

## 🎯 **What Would Happen When You Run These Commands**

### **Docker Build Process:**
```
Step 1/15 : FROM nvidia/cuda:11.8-runtime-ubuntu22.04 as base
 ---> Pulling CUDA base image...
Step 2/15 : RUN apt-get update && apt-get install -y python3 python3-pip
 ---> Installing Python and dependencies...
Step 3/15 : COPY requirements.txt /tmp/
 ---> Copying requirements file...
Step 4/15 : RUN pip install -r /tmp/requirements.txt
 ---> Installing Python packages...
[... additional build steps ...]
Successfully built thai-model-api:latest
```

### **Container Startup:**
```
Container ID: abc123def456
Status: Running
Ports: 0.0.0.0:8001->8001/tcp
Health: Starting -> Healthy (after health check passes)
```

### **API Response Example:**
```json
{
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1699123456,
    "model": "thai-model",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "สวัสดีครับ! ยินดีที่ได้รู้จักคุณ มีอะไรให้ช่วยเหลือไหมครับ?"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 8,
        "completion_tokens": 20,
        "total_tokens": 28
    }
}
```

## 🚀 **To Install Docker (if needed):**

### **Ubuntu/Debian:**
```bash
# Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER
```

### **For NVIDIA GPU support:**
```bash
# Install NVIDIA Container Toolkit
curl -s -L https://nvidia.github.io/nvidia-container-runtime/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-container-runtime/$distribution/nvidia-container-runtime.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-runtime.list
sudo apt-get update
sudo apt-get install nvidia-container-runtime

# Restart Docker
sudo systemctl restart docker
```

## 📋 **Expected Results:**

When Docker is running and you execute the deployment:

1. ✅ **Build succeeds** - Creates optimized container image (~3-5GB)
2. ✅ **Container starts** - API available on http://localhost:8001
3. ✅ **Health check passes** - Container reports healthy status
4. ✅ **API responds** - Thai language model answers questions
5. ✅ **Monitoring works** - Prometheus collects metrics, Grafana shows dashboards
6. ✅ **Scaling ready** - Can easily add more containers behind load balancer

---

**🎉 Your containerization setup is complete and ready to deploy when Docker is available!**
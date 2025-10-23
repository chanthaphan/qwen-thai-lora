# Docker Deployment Guide
# Thai Language Model Project

## 📚 Lesson 8: Container Deployment

Welcome to the final lesson of our Thai Language Model project! In this lesson, you'll learn how to containerize and deploy your AI model using Docker. This is essential for production deployments, scaling, and ensuring consistent environments across different systems.

## 🎯 Learning Objectives

By the end of this lesson, you will:
- Understand Docker containerization concepts
- Build multi-stage Docker images for AI models
- Configure production-ready container orchestration
- Deploy with monitoring and reverse proxy
- Manage containerized AI applications

## 📋 Prerequisites

- ✅ Completed Lessons 1-7 (Project setup through Hosting)
- ✅ Docker installed and running
- ✅ NVIDIA Docker support (optional, for GPU acceleration)
- ✅ Working Thai model API from previous lessons

## 🐳 Docker Fundamentals for AI Models

### Why Containerize AI Models?

1. **Consistency**: Same environment across development, testing, and production
2. **Isolation**: Dependencies and libraries contained within the container
3. **Scalability**: Easy to scale horizontally with orchestration tools
4. **Portability**: Run anywhere Docker is supported
5. **Reproducibility**: Exact same environment every time

### Docker Components for AI

```
┌─────────────────────────────────────────────────┐
│                Docker Image                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────┐ │
│  │ Base OS     │  │ Python +     │  │ Your   │ │
│  │ (Ubuntu)    │  │ Dependencies │  │ Model  │ │
│  └─────────────┘  └──────────────┘  └────────┘ │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│              Docker Container                   │
│        (Running instance of image)              │
│                                               │
│  ┌─────────┐ ┌──────────┐ ┌─────────────────┐  │
│  │ Volume  │ │ Network  │ │ Resource Limits │  │
│  │ Mounts  │ │ Config   │ │ CPU/GPU/Memory  │  │
│  └─────────┘ └──────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 🏗️ Multi-Stage Dockerfile Architecture

Our Dockerfile uses a multi-stage build for optimization:

### Stage 1: Base Environment
```dockerfile
FROM nvidia/cuda:11.8-runtime-ubuntu22.04 as base
# Sets up CUDA and basic system
```

### Stage 2: Dependencies
```dockerfile
FROM base as dependencies
# Installs Python packages and system dependencies
```

### Stage 3: Application
```dockerfile
FROM dependencies as application
# Copies application code and sets up runtime
```

### Benefits of Multi-Stage Builds

1. **Smaller final images**: Build tools not included in final image
2. **Better caching**: Each stage can be cached independently
3. **Security**: Minimal attack surface in production image
4. **Flexibility**: Can build different targets for different purposes

## 🚀 Building Your First Container

### Step 1: Build the Image

```bash
# Build the complete application image
docker build -t thai-model-api:latest . --target application

# View the built image
docker images thai-model-api:latest
```

### Step 2: Run the Container

```bash
# Run with GPU support (if available)
docker run -d \
    --name thai-model-api \
    --gpus all \
    -p 8001:8001 \
    -v ./models:/app/models:ro \
    -v ./config:/app/config:ro \
    thai-model-api:latest

# Run CPU-only mode
docker run -d \
    --name thai-model-api \
    -p 8001:8001 \
    -v ./models:/app/models:ro \
    -v ./config:/app/config:ro \
    thai-model-api:latest
```

### Step 3: Test the Container

```bash
# Health check
curl http://localhost:8001/health

# Test API
curl -X POST http://localhost:8001/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "thai-model",
        "messages": [{"role": "user", "content": "สวัสดี"}],
        "max_tokens": 50
    }'
```

## 🎼 Docker Compose Orchestration

### Development Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  thai-model-api:
    build: .
    ports:
      - "8001:8001"
    volumes:
      - ./models:/app/models:ro
    environment:
      - CUDA_VISIBLE_DEVICES=0
```

### Production Setup

Our production setup includes:

1. **Main API Service**: Your Thai model API
2. **Nginx Reverse Proxy**: Load balancing and SSL termination
3. **Prometheus**: Metrics collection
4. **Grafana**: Monitoring dashboards
5. **Redis**: Caching layer (optional)

```bash
# Start production stack
docker-compose up -d

# View running services
docker-compose ps

# View logs
docker-compose logs -f thai-model-api
```

## 📊 Container Monitoring

### Health Checks

Our containers include health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8001/health || exit 1
```

### Metrics Collection

- **API Metrics**: Response times, request counts, error rates
- **System Metrics**: CPU, memory, GPU utilization
- **Container Metrics**: Resource usage per container

### Monitoring Stack

```
User Request → Nginx → Thai Model API → Metrics → Prometheus → Grafana
                ↓            ↓              ↓
            Rate Limit   Health Check   Alerting
```

## 🔒 Security Best Practices

### Container Security

1. **Non-root user**: Runs as non-privileged user
2. **Read-only mounts**: Model files mounted read-only
3. **Resource limits**: CPU/Memory limits defined
4. **Network isolation**: Services communicate through internal networks

### Access Control

1. **Rate limiting**: Nginx limits requests per IP
2. **API authentication**: JWT tokens (can be added)
3. **Network policies**: Restricted container communication
4. **SSL/TLS**: HTTPS for production (nginx configuration ready)

## 🎯 Practical Exercise

Let's run the automated Docker demonstration:

```bash
# Run the complete Docker deployment demo
./docker-demo.sh
```

This script will:
1. ✅ Check Docker availability
2. ✅ Test GPU support
3. ✅ Build the Docker image
4. ✅ Run a test container
5. ✅ Perform API tests
6. ✅ Show monitoring information

## 🔧 Troubleshooting Common Issues

### Build Issues

```bash
# Clear Docker cache
docker system prune -f

# Build with no cache
docker build --no-cache -t thai-model-api:latest .

# Check build logs
docker build -t thai-model-api:latest . --progress=plain
```

### Runtime Issues

```bash
# Check container logs
docker logs thai-model-api

# Get inside container for debugging
docker exec -it thai-model-api /bin/bash

# Check resource usage
docker stats thai-model-api
```

### GPU Issues

```bash
# Test NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi

# Check CUDA in container
docker exec -it thai-model-api nvidia-smi
```

## 📈 Production Deployment Strategies

### 1. Single Server Deployment

```bash
# Simple production deployment
docker-compose -f docker-compose.yml up -d
```

### 2. Multi-Server Deployment (Docker Swarm)

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml thai-model-stack
```

### 3. Kubernetes Deployment

```yaml
# kubernetes-deployment.yml example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: thai-model-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: thai-model-api
  template:
    metadata:
      labels:
        app: thai-model-api
    spec:
      containers:
      - name: thai-model-api
        image: thai-model-api:latest
        ports:
        - containerPort: 8001
```

## 🎓 Lesson Summary

Congratulations! You've completed the Docker Deployment lesson. You now know how to:

### ✅ What You've Learned

1. **Docker Fundamentals**: Understanding containers vs images
2. **Multi-Stage Builds**: Optimizing Docker images for AI models
3. **Container Orchestration**: Using docker-compose for multi-service deployments
4. **Production Setup**: Nginx, monitoring, and security configurations
5. **Troubleshooting**: Debugging containerized applications
6. **Deployment Strategies**: From single server to Kubernetes

### 🎯 Key Takeaways

1. **Consistency is King**: Containers ensure your model runs the same everywhere
2. **Security by Default**: Use non-root users and read-only mounts
3. **Monitor Everything**: Health checks and metrics are essential
4. **Plan for Scale**: Design for horizontal scaling from the start

### 🚀 Next Steps

You've now completed all 8 lessons of the Thai Language Model project! You have:

1. ✅ **Project Foundation** - Set up the complete development environment
2. ✅ **Model Training** - Fine-tuned your own Thai language model
3. ✅ **Testing & Validation** - Verified model performance
4. ✅ **API Development** - Created production-ready APIs
5. ✅ **Interface Design** - Built user-friendly interfaces
6. ✅ **Deployment** - Containerized for production use

### 🌟 Production Checklist

Before deploying to production:

- [ ] SSL certificates configured
- [ ] Database backups scheduled
- [ ] Monitoring alerts set up
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation updated
- [ ] Team training completed

## 🔗 Additional Resources

- [Docker Best Practices for AI/ML](https://docs.docker.com)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)
- [Kubernetes for ML Workloads](https://kubernetes.io/docs/concepts/workloads/)
- [Container Security Guide](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

---

**🎉 Congratulations on completing the Thai Language Model project!**

You're now ready to deploy AI models in production environments using modern containerization practices.
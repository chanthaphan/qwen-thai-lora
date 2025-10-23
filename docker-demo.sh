#!/bin/bash

# Docker Deployment Demo Script for Thai Model
# ===============================================

set -e  # Exit on any error

echo "🐳 Thai Model Docker Deployment Demo"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "\n${BLUE}📋 Step $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is available
print_step 1 "Checking Docker availability"
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    exit 1
fi

print_success "Docker is available and running"

# Check for NVIDIA Docker support
print_step 2 "Checking NVIDIA Docker support"
if docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    print_success "NVIDIA Docker support is available"
    GPU_SUPPORT=true
else
    print_warning "NVIDIA Docker support not available - will use CPU-only mode"
    GPU_SUPPORT=false
fi

# Build the Docker image
print_step 3 "Building Thai Model Docker image"
echo "Building multi-stage Docker image..."

# Use CPU-only Dockerfile since NVIDIA Docker support is not available
if [ "$GPU_SUPPORT" = true ]; then
    docker build -t thai-model-api:latest . --target application
else
    echo "Using CPU-only Dockerfile..."
    docker build -f Dockerfile.cpu -t thai-model-api:latest . --target application
fi

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Show image info
print_step 4 "Inspecting built image"
docker images thai-model-api:latest
echo ""
docker inspect thai-model-api:latest | jq '.[0].Config.Labels // "No labels"'

# Run container in test mode
print_step 5 "Running container in test mode"

# Stop any existing containers
docker stop thai-model-api-test 2>/dev/null || true
docker rm thai-model-api-test 2>/dev/null || true

if [ "$GPU_SUPPORT" = true ]; then
    echo "Starting with GPU support..."
    docker run -d \
        --name thai-model-api-test \
        --gpus all \
        -p 8002:8001 \
        -e CUDA_VISIBLE_DEVICES=0 \
        -v "$(pwd)/models:/app/models:ro" \
        -v "$(pwd)/config:/app/config:ro" \
        --restart unless-stopped \
        thai-model-api:latest
else
    echo "Starting in CPU-only mode..."
    docker run -d \
        --name thai-model-api-test \
        -p 8002:8001 \
        -v "$(pwd)/models:/app/models:ro" \
        -v "$(pwd)/config:/app/config:ro" \
        --restart unless-stopped \
        thai-model-api:latest
fi

print_success "Container started on port 8002"

# Wait for container to be ready
print_step 6 "Waiting for API to be ready"
echo "Waiting for health check..."

for i in {1..30}; do
    if curl -f http://localhost:8002/health &> /dev/null; then
        print_success "API is responding"
        break
    fi
    echo -n "."
    sleep 2
done

if ! curl -f http://localhost:8002/health &> /dev/null; then
    print_error "API failed to start within timeout"
    echo "Container logs:"
    docker logs thai-model-api-test
    exit 1
fi

# Test the API
print_step 7 "Testing containerized API"
echo "Testing health endpoint..."
curl -s http://localhost:8002/health | jq '.'

echo -e "\nTesting chat completion..."
curl -s -X POST http://localhost:8002/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "thai-model",
        "messages": [
            {"role": "user", "content": "สวัสดี"}
        ],
        "max_tokens": 50,
        "stream": false
    }' | jq '.choices[0].message.content'

# Show container stats
print_step 8 "Container statistics"
docker stats thai-model-api-test --no-stream

# Show running containers
echo -e "\nRunning containers:"
docker ps --filter name=thai-model

print_success "Docker deployment test completed successfully!"

echo -e "\n${BLUE}🎯 Docker Deployment Options:${NC}"
echo "1. Single container: docker run thai-model-api:latest"
echo "2. Development: docker-compose up"
echo "3. Production: docker-compose -f docker-compose.prod.yml up -d"
echo "4. Test current: curl http://localhost:8002/health"

echo -e "\n${BLUE}🔧 Management Commands:${NC}"
echo "• View logs: docker logs thai-model-api-test"
echo "• Stop test: docker stop thai-model-api-test"
echo "• Cleanup: docker rm thai-model-api-test"
echo "• Remove image: docker rmi thai-model-api:latest"

print_warning "Remember to stop the test container: docker stop thai-model-api-test"
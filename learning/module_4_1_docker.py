#!/usr/bin/env python3
"""
Module 4.1: Docker Mastery
=========================

Interactive learning script for containerization with Docker, including
multi-stage builds, optimization, and orchestration.
"""

import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎓 {title}")
    print(f"{'='*60}\n")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"📚 Step {step_num}: {description}")
    print("-" * 40)

def explain_docker_basics():
    """Explain Docker fundamentals."""
    print("""
🐳 Docker Fundamentals for ML Applications:

🌟 Why Docker for ML?
   • Reproducible environments across dev/staging/prod
   • Dependency isolation (no more "works on my machine")
   • Easy scaling and deployment
   • Version control for entire application stack
   • GPU support for accelerated inference

🏗️ Core Docker Concepts:

1. 📦 Images vs Containers:
   ```bash
   # Image = Blueprint (immutable)
   docker build -t thai-model:v1.0 .
   
   # Container = Running instance (stateful)
   docker run -p 8000:8000 thai-model:v1.0
   ```

2. 📋 Dockerfile Anatomy:
   ```dockerfile
   # Base image with Python and CUDA support
   FROM nvidia/cuda:11.8-devel-ubuntu20.04
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \\
       python3 python3-pip git curl \\
       && rm -rf /var/lib/apt/lists/*
   
   # Set working directory
   WORKDIR /app
   
   # Copy and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   # Install the package
   RUN pip install -e .
   
   # Expose port
   EXPOSE 8000
   
   # Set entry point
   CMD ["python", "scripts/api_server.py"]
   ```

3. 🔧 Build Context & .dockerignore:
   ```bash
   # .dockerignore - exclude unnecessary files
   __pycache__/
   *.pyc
   .git/
   .vscode/
   *.log
   tests/
   .pytest_cache/
   llm-env/  # Don't copy virtual environment
   ```

🎯 Docker Best Practices:
   • Use official base images
   • Minimize layers and image size
   • Use multi-stage builds for production
   • Don't run as root user
   • Use .dockerignore effectively
   • Cache dependencies separately from code
""")

def analyze_thai_model_dockerfiles():
    """Analyze the actual Dockerfiles in the project."""
    print("""
🔍 Thai Model Docker Implementation Analysis:
""")
    
    project_root = Path(__file__).parent.parent
    docker_dir = project_root / "deployment" / "docker"
    
    dockerfiles = {
        "Dockerfile": "🏭 Production GPU-enabled image",
        "Dockerfile.cpu": "💻 CPU-optimized image for development"
    }
    
    for dockerfile_name, description in dockerfiles.items():
        dockerfile_path = docker_dir / dockerfile_name
        
        if dockerfile_path.exists():
            print(f"\n📄 {dockerfile_name}: {description}")
            
            with open(dockerfile_path, 'r') as f:
                content = f.read()
            
            # Analyze key components
            analysis = {
                'FROM': 'Base image',
                'RUN': 'Build commands',
                'COPY': 'File operations', 
                'EXPOSE': 'Port exposure',
                'CMD': 'Default command',
                'WORKDIR': 'Working directory',
                'ENV': 'Environment variables',
                'USER': 'Security (non-root user)'
            }
            
            print(f"  📊 Components found:")
            for instruction, description in analysis.items():
                count = content.count(instruction)
                if count > 0:
                    print(f"    • {instruction}: {count} ({description})")
            
            # Show optimization techniques
            optimizations = {
                'Multi-stage': 'FROM' in content and content.count('FROM') > 1,
                'Layer caching': 'COPY requirements.txt' in content,
                'Cleanup': 'rm -rf /var/lib/apt/lists/*' in content,
                'Non-root user': 'USER' in content,
                'Health check': 'HEALTHCHECK' in content
            }
            
            print(f"  ✅ Optimizations applied:")
            for opt, present in optimizations.items():
                status = "✅" if present else "❌"
                print(f"    {status} {opt}")
        else:
            print(f"\n❌ {dockerfile_name} not found at {dockerfile_path}")

def explain_multistage_builds():
    """Explain multi-stage Docker builds."""
    print("""
🏗️ Multi-Stage Docker Builds:

💡 Why Multi-Stage?
   • Separate build dependencies from runtime
   • Smaller production images (security + performance)
   • Keep development tools out of production
   • Cache intermediate stages for faster builds

🎯 ML Model Multi-Stage Pattern:

```dockerfile
# Stage 1: Build environment with all tools
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \\
    gcc g++ make cmake \\
    git curl wget

WORKDIR /app

# Install Python build dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Build custom wheels if needed
COPY setup.py .
RUN pip install --user .

#==========================================
# Stage 2: Runtime environment (minimal)
FROM python:3.11-slim as runtime

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\  # For health checks
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
WORKDIR /home/app
USER app

# Copy application code
COPY --chown=app:app . .

# Make sure Python packages are in PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "thai_model.api.fastapi_server:app", "--host", "0.0.0.0"]
```

📊 Size Comparison:
   • Single-stage: ~2.5GB (includes build tools)
   • Multi-stage: ~800MB (runtime only)
   • Savings: ~70% smaller image

🚀 Advanced Multi-Stage Patterns:

1. 🧪 Development vs Production:
   ```dockerfile
   # Development stage with debugging tools
   FROM runtime as development
   USER root
   RUN pip install --no-cache-dir pytest ipdb debugpy
   USER app
   CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "..."]
   
   # Production stage (lean)
   FROM runtime as production
   CMD ["gunicorn", "thai_model.api.fastapi_server:app", "-c", "gunicorn_config.py"]
   ```

2. 🔧 Model Download Stage:
   ```dockerfile
   # Stage for downloading large ML models
   FROM python:3.11-slim as model-downloader
   RUN pip install huggingface-hub
   WORKDIR /models
   RUN python -c "
   from huggingface_hub import snapshot_download
   snapshot_download('Qwen/Qwen2.5-1.5B-Instruct', local_dir='./qwen')
   "
   
   # Copy models to final stage
   FROM runtime as final
   COPY --from=model-downloader /models /app/models
   ```
""")

def explain_docker_compose():
    """Explain Docker Compose for multi-service orchestration."""
    print("""
🎼 Docker Compose Orchestration:

🌟 Why Docker Compose?
   • Multi-service applications (API + Redis + Database)
   • Environment-specific configurations
   • Service discovery and networking
   • Volume management for persistence
   • Easy local development setup

📋 Thai Model Compose Architecture:

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Main API service
  thai-api:
    build:
      context: .
      dockerfile: deployment/docker/Dockerfile.cpu
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=info
    depends_on:
      - redis
    volumes:
      - ./models:/app/models  # Mount local models
      - ./logs:/app/logs      # Persist logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Redis for caching and rate limiting
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./deployment/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - thai-api
    restart: unless-stopped

  # Prometheus monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  # Grafana dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: thai-model-network
```

🔧 Environment-Specific Overrides:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  thai-api:
    image: thai-model:production
    environment:
      - WORKERS=4
      - LOG_LEVEL=warning
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  nginx:
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt  # SSL certificates
```

🚀 Compose Commands:
```bash
# Development
docker-compose up -d

# Production  
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scaling
docker-compose up --scale thai-api=3

# Logs
docker-compose logs -f thai-api

# Health check
docker-compose ps
```
""")

def explain_optimization_techniques():
    """Explain Docker optimization techniques."""
    print("""
⚡ Docker Optimization for ML Applications:

🎯 Image Size Optimization:

1. 📦 Distroless Images:
   ```dockerfile
   # Use Google's distroless images (no shell, minimal attack surface)
   FROM gcr.io/distroless/python3-debian11
   
   # Copy Python packages and app
   COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
   COPY --from=builder /app /app
   
   # Only has Python runtime, no shell or package managers
   ENTRYPOINT ["python", "-m", "thai_model.api.fastapi_server"]
   ```

2. 🧹 Layer Optimization:
   ```dockerfile
   # ❌ Bad: Multiple RUN commands create many layers
   RUN apt-get update
   RUN apt-get install -y python3
   RUN apt-get install -y pip
   RUN rm -rf /var/lib/apt/lists/*
   
   # ✅ Good: Single RUN command with cleanup
   RUN apt-get update && apt-get install -y \\
       python3 pip \\
       && rm -rf /var/lib/apt/lists/* \\
       && apt-get clean
   ```

3. 📋 Dependency Caching:
   ```dockerfile
   # ✅ Copy requirements first for better caching
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy source code (changes frequently)
   COPY . .
   ```

🚀 Performance Optimization:

1. 🔧 Build Args for Flexibility:
   ```dockerfile
   ARG PYTHON_VERSION=3.11
   ARG TORCH_VERSION=2.1.0
   ARG CUDA_VERSION=11.8
   
   FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu20.04
   
   # Install specific Python version
   RUN apt-get update && apt-get install -y \\
       python${PYTHON_VERSION} \\
       python${PYTHON_VERSION}-pip
   
   # Install specific PyTorch
   RUN pip install torch==${TORCH_VERSION}
   ```

2. 🏃 Init System for Graceful Shutdown:
   ```dockerfile
   # Use tini for proper signal handling
   RUN apt-get install -y tini
   ENTRYPOINT ["tini", "--"]
   CMD ["python", "-m", "thai_model.api.fastapi_server"]
   ```

3. 💾 Volume Mounting for Models:
   ```dockerfile
   # Create mount points for external model storage
   RUN mkdir -p /app/models /app/cache
   VOLUME ["/app/models", "/app/cache"]
   
   # Environment variables for paths
   ENV MODEL_PATH=/app/models
   ENV CACHE_PATH=/app/cache
   ```

🔒 Security Best Practices:

1. 👤 Non-Root User:
   ```dockerfile
   # Create dedicated user
   RUN groupadd -r appgroup && useradd -r -g appgroup appuser
   
   # Set ownership
   CHOWN appuser:appgroup /app
   USER appuser
   
   # Drop privileges
   USER 1000:1000
   ```

2. 🛡️ Security Scanning:
   ```bash
   # Scan for vulnerabilities
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
     aquasec/trivy image thai-model:latest
   
   # Bench for CIS compliance
   docker run --rm --net host --pid host --userns host --cap-add audit_control \\
     -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \\
     -v /var/lib:/var/lib \\
     -v /var/run/docker.sock:/var/run/docker.sock \\
     docker/docker-bench-security
   ```

⚡ Runtime Optimization:
   • Use init systems (tini) for proper signal handling
   • Set resource limits (memory, CPU)
   • Configure proper logging drivers
   • Use health checks for reliability
   • Implement graceful shutdown handling
""")

def main():
    print_header("Module 4.1: Docker Mastery")
    
    # Step 1: Docker Basics
    print_step(1, "Docker Fundamentals for ML Applications")
    explain_docker_basics()
    
    input("\n🔍 Press Enter to analyze Thai Model Dockerfiles...")
    
    # Step 2: Analyze Existing Dockerfiles
    print_step(2, "Thai Model Docker Implementation")
    analyze_thai_model_dockerfiles()
    
    input("\n🔍 Press Enter to learn about multi-stage builds...")
    
    # Step 3: Multi-Stage Builds
    print_step(3, "Multi-Stage Docker Builds")
    explain_multistage_builds()
    
    input("\n🔍 Press Enter to learn about Docker Compose...")
    
    # Step 4: Docker Compose
    print_step(4, "Docker Compose Orchestration")
    explain_docker_compose()
    
    input("\n🔍 Press Enter to learn optimization techniques...")
    
    # Step 5: Optimization
    print_step(5, "Docker Optimization Techniques") 
    explain_optimization_techniques()
    
    input("\n🔍 Press Enter to see practical exercises...")
    
    # Step 6: Practical Exercises
    print_step(6, "Docker Mastery Exercises")
    
    print("""
🧪 Hands-on Docker Experiments:

1. 🏗️ Build Thai Model Images:
   ```bash
   cd /home/chanthaphan/project
   
   # Build CPU-optimized image
   docker build -f deployment/docker/Dockerfile.cpu -t thai-model:cpu .
   
   # Build GPU-enabled image (if CUDA available)
   docker build -f deployment/docker/Dockerfile -t thai-model:gpu .
   
   # Check image sizes
   docker images | grep thai-model
   ```

2. 🚀 Run Containerized API:
   ```bash
   # Run CPU version
   docker run -p 8000:8000 \\
     -e LOG_LEVEL=debug \\
     -v $(pwd)/models:/app/models \\
     thai-model:cpu
   
   # Test the API
   curl http://localhost:8000/health
   curl http://localhost:8000/v1/models
   ```

3. 🎼 Multi-Service Setup with Compose:
   ```bash
   # Start the full stack
   cd deployment/docker
   docker-compose up -d
   
   # Check all services
   docker-compose ps
   
   # View logs
   docker-compose logs -f thai-api
   
   # Scale the API
   docker-compose up --scale thai-api=3 -d
   ```

4. 🔍 Container Inspection:
   ```bash
   # Inspect running container
   docker ps
   docker inspect <container_id>
   
   # Check resource usage
   docker stats
   
   # Execute commands in container
   docker exec -it <container_id> /bin/bash
   
   # View container logs
   docker logs -f <container_id>
   ```

5. 🛠️ Image Optimization Exercise:
   ```dockerfile
   # Create optimized Dockerfile
   # File: Dockerfile.optimized
   
   # Multi-stage build
   FROM python:3.11-slim as base
   
   # Install system deps in one layer
   RUN apt-get update && apt-get install -y \\
       curl gcc g++ \\
       && rm -rf /var/lib/apt/lists/* \\
       && apt-get clean
   
   FROM base as builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --user --no-cache-dir -r requirements.txt
   
   FROM base as runtime
   
   # Create non-root user
   RUN useradd --create-home app
   
   # Copy installed packages
   COPY --from=builder /root/.local /home/app/.local
   
   # Copy application
   WORKDIR /home/app
   COPY --chown=app:app . .
   
   USER app
   ENV PATH=/home/app/.local/bin:$PATH
   
   # Health check
   HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health
   
   EXPOSE 8000
   CMD ["python", "-m", "uvicorn", "thai_model.api.fastapi_server:app", "--host", "0.0.0.0"]
   ```

6. 📊 Performance Benchmarking:
   ```bash
   # Compare image sizes
   docker images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}" | grep thai-model
   
   # Benchmark startup time
   time docker run --rm thai-model:cpu python -c "
   from thai_model.api.fastapi_server import app
   print('API loaded successfully')
   "
   
   # Memory usage comparison
   docker run --rm -m 1g thai-model:cpu python -c "
   import psutil
   print(f'Memory usage: {psutil.virtual_memory().percent}%')
   "
   ```

7. 🔒 Security Assessment:
   ```bash
   # Scan for vulnerabilities (install trivy first)
   trivy image thai-model:cpu
   
   # Check for best practices
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
     goodwithtech/dockle thai-model:cpu
   
   # Verify non-root user
   docker run --rm thai-model:cpu whoami
   docker run --rm thai-model:cpu id
   ```

8. 🌐 Production Deployment:
   ```bash
   # Production compose with overrides
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   
   # Health check all services
   docker-compose exec thai-api curl http://localhost:8000/health
   
   # Monitor resource usage
   docker-compose top
   
   # Rolling updates
   docker-compose up -d --no-deps thai-api
   ```

🎯 Advanced Docker Topics:

📦 Container Registries:
   ```bash
   # Tag for registry
   docker tag thai-model:cpu your-registry.com/thai-model:v1.0
   
   # Push to registry
   docker push your-registry.com/thai-model:v1.0
   
   # Pull and run from registry
   docker run your-registry.com/thai-model:v1.0
   ```

☸️ Kubernetes Preparation:
   ```yaml
   # k8s-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: thai-model
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: thai-model
     template:
       metadata:
         labels:
           app: thai-model
       spec:
         containers:
         - name: api
           image: thai-model:cpu
           ports:
           - containerPort: 8000
           resources:
             requests:
               memory: "1Gi"
               cpu: "500m"
             limits:
               memory: "2Gi"
               cpu: "1000m"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
           readinessProbe:
             httpGet:
               path: /ready
               port: 8000
   ```

🔄 CI/CD Integration:
   ```yaml
   # .github/workflows/docker.yml
   name: Docker Build and Deploy
   
   on:
     push:
       branches: [main]
   
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v3
       
       - name: Build Docker image
         run: |
           docker build -f deployment/docker/Dockerfile.cpu \\
             -t thai-model:${{ github.sha }} .
       
       - name: Run tests in container
         run: |
           docker run --rm thai-model:${{ github.sha }} \\
             python -m pytest tests/
       
       - name: Push to registry
         run: |
           echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
           docker push thai-model:${{ github.sha }}
   ```

🎯 Key Takeaways:
   • Multi-stage builds reduce image size and attack surface
   • Docker Compose simplifies multi-service orchestration
   • Proper optimization improves performance and security
   • Container registries enable scalable deployment
   • Health checks and monitoring are essential for production

🚀 Ready for Module 4.2: Production Deployment!
""")

if __name__ == "__main__":
    main()
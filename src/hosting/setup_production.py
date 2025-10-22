#!/usr/bin/env python3
"""
Production Deployment Script
Setup for production hosting of Thai model API
"""

import os
import subprocess
import sys
from pathlib import Path

def create_systemd_service():
    """Create systemd service file for production deployment"""
    
    current_dir = Path.cwd()
    user = os.getenv("USER")
    
    service_content = f"""[Unit]
Description=Thai Model FastAPI Server
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={current_dir}
Environment=PATH={current_dir}/llm-env/bin
ExecStart={current_dir}/llm-env/bin/python {current_dir}/src/hosting/fastapi_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "thai-model-api.service"
    
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"✅ Created systemd service file: {service_file}")
    print("\n🔧 To install and start the service:")
    print(f"   sudo cp {service_file} /etc/systemd/system/")
    print("   sudo systemctl daemon-reload")
    print("   sudo systemctl enable thai-model-api")
    print("   sudo systemctl start thai-model-api")
    print("   sudo systemctl status thai-model-api")
    
    return service_file

def create_nginx_config():
    """Create nginx configuration for reverse proxy"""
    
    nginx_content = """# Thai Model API Nginx Configuration
server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for model inference
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization";
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
    }
    
    # Serve API documentation
    location /docs {
        proxy_pass http://127.0.0.1:8001/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8001/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        access_log off;
    }
}

# HTTPS configuration (after getting SSL certificate)
# server {
#     listen 443 ssl http2;
#     server_name your-domain.com;
#     
#     ssl_certificate /path/to/your/certificate.pem;
#     ssl_certificate_key /path/to/your/private-key.pem;
#     
#     # Include the same location blocks as above
# }
"""
    
    nginx_file = "thai-model-api.nginx"
    
    with open(nginx_file, 'w') as f:
        f.write(nginx_content)
    
    print(f"✅ Created nginx configuration: {nginx_file}")
    print("\n🔧 To install nginx configuration:")
    print(f"   sudo cp {nginx_file} /etc/nginx/sites-available/thai-model-api")
    print("   sudo ln -s /etc/nginx/sites-available/thai-model-api /etc/nginx/sites-enabled/")
    print("   sudo nginx -t")
    print("   sudo systemctl reload nginx")
    
    return nginx_file

def create_docker_compose():
    """Create docker-compose.yml for containerized deployment"""
    
    compose_content = """version: '3.8'

services:
  thai-model-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./models:/app/models:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro  # Mount SSL certificates
    depends_on:
      - thai-model-api
    restart: unless-stopped

  # Optional: Monitoring with Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    restart: unless-stopped

  # Optional: Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
    restart: unless-stopped

volumes:
  grafana-storage:
"""
    
    compose_file = "docker-compose.prod.yml"
    
    with open(compose_file, 'w') as f:
        f.write(compose_content)
    
    print(f"✅ Created Docker Compose configuration: {compose_file}")
    print("\n🔧 To deploy with Docker Compose:")
    print("   docker-compose -f docker-compose.prod.yml up -d")
    print("   docker-compose -f docker-compose.prod.yml logs -f")
    
    return compose_file

def create_monitoring_config():
    """Create monitoring configuration"""
    
    # Create monitoring directory
    os.makedirs("monitoring", exist_ok=True)
    
    # Prometheus configuration
    prometheus_content = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'thai-model-api'
    static_configs:
      - targets: ['thai-model-api:8001']
    scrape_interval: 5s
    metrics_path: '/metrics'

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    scrape_interval: 10s
"""
    
    with open("monitoring/prometheus.yml", 'w') as f:
        f.write(prometheus_content)
    
    print("✅ Created monitoring configuration: monitoring/prometheus.yml")

def create_startup_script():
    """Create startup script for development/testing"""
    
    startup_content = """#!/bin/bash

# Thai Model API Startup Script
# This script sets up and starts the Thai model API server

set -e  # Exit on error

echo "🚀 Thai Model API Startup"
echo "========================"

# Check if virtual environment exists
if [ ! -d "llm-env" ]; then
    echo "❌ Virtual environment not found"
    echo "Run: python -m venv llm-env && ./llm-env/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if model exists
if [ ! -d "models/qwen_thai_lora" ]; then
    echo "❌ Thai model not found at models/qwen_thai_lora"
    echo "Please run training first: ./manage.sh train"
    exit 1
fi

# Check if port is available
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8001 is already in use"
    echo "Stop existing server or use a different port"
    exit 1
fi

# Set environment variables
export PYTHONPATH="${PWD}:${PYTHONPATH}"
export CUDA_VISIBLE_DEVICES=0  # Use first GPU

echo "✅ Environment checks passed"
echo "📁 Model path: models/qwen_thai_lora"
echo "🐍 Python: $(./llm-env/bin/python --version)"
echo "🌐 Starting server on http://localhost:8001"
echo "📚 API docs: http://localhost:8001/docs"
echo ""

# Start the server
exec ./llm-env/bin/python src/hosting/fastapi_server.py
"""
    
    with open("start_api.sh", 'w') as f:
        f.write(startup_content)
    
    # Make executable
    os.chmod("start_api.sh", 0o755)
    
    print("✅ Created startup script: start_api.sh")
    print("   Usage: ./start_api.sh")

def main():
    """Main deployment setup function"""
    print("🏭 Thai Model Production Deployment Setup")
    print("=" * 50)
    
    print("\n1. Creating systemd service file...")
    service_file = create_systemd_service()
    
    print("\n2. Creating nginx configuration...")
    nginx_file = create_nginx_config()
    
    print("\n3. Creating Docker Compose configuration...")
    compose_file = create_docker_compose()
    
    print("\n4. Creating monitoring configuration...")
    create_monitoring_config()
    
    print("\n5. Creating startup script...")
    create_startup_script()
    
    print(f"\n🎉 Production deployment files created!")
    print(f"\n📁 Files created:")
    print(f"   • {service_file} - Systemd service")
    print(f"   • {nginx_file} - Nginx reverse proxy")
    print(f"   • {compose_file} - Docker Compose")
    print(f"   • monitoring/prometheus.yml - Monitoring")
    print(f"   • start_api.sh - Development startup")
    
    print(f"\n🚀 Quick Start Options:")
    print(f"   Development: ./start_api.sh")
    print(f"   Docker: docker-compose -f {compose_file} up")
    print(f"   Production: Install systemd service and nginx")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Test locally: ./start_api.sh")
    print(f"   2. Configure domain and SSL certificates")
    print(f"   3. Set up monitoring and logging")
    print(f"   4. Deploy to production server")

if __name__ == "__main__":
    main()
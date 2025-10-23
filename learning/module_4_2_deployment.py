#!/usr/bin/env python3
"""
Module 4.2: Production Deployment
===============================

Interactive learning script for production deployment strategies including
Nginx, systemd, monitoring, and DevOps best practices.
"""

import sys
import os
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

def explain_production_architecture():
    """Explain production deployment architecture."""
    print("""
🏭 Production Architecture for ML APIs:

🌟 Production Stack Components:

┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                   (AWS ALB/Nginx)                       │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                Reverse Proxy                            │
│                 (Nginx/Traefik)                         │
│  • SSL Termination  • Rate Limiting  • Caching         │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              API Gateway (Optional)                     │
│           (Kong/AWS API Gateway)                        │
│  • Authentication  • Analytics  • Versioning           │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│            Thai Model API Instances                     │
│              (Multiple Workers)                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │ Worker 1│  │ Worker 2│  │ Worker 3│                │
│  └─────────┘  └─────────┘  └─────────┘                │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│               Support Services                          │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐     │
│  │  Redis  │ │PostgreSQL│ │Prometheus│ │ Grafana │     │
│  │ (Cache) │ │ (Metadata│ │(Metrics) │ │(Dashbrd)│     │
│  └─────────┘ └──────────┘ └─────────┘ └─────────┘     │
└─────────────────────────────────────────────────────────┘

🎯 Key Design Principles:

1. 🔄 Redundancy: Multiple instances, no single points of failure
2. 📈 Scalability: Horizontal scaling with load balancing
3. 🛡️ Security: Defense in depth, SSL/TLS, authentication layers
4. 📊 Observability: Comprehensive logging, metrics, tracing
5. 🚀 Performance: Caching, connection pooling, optimization
6. 🔧 Maintainability: Infrastructure as code, automated deployment

💡 Deployment Strategies:

1. 🟦 Blue-Green Deployment:
   • Two identical production environments
   • Switch traffic instantly between versions
   • Zero-downtime deployments
   • Easy rollback capability

2. 🌊 Rolling Deployment:
   • Gradual replacement of instances
   • Maintains service availability
   • Lower resource requirements
   • Progressive risk mitigation

3. 🎯 Canary Deployment:
   • Route small percentage to new version
   • Monitor metrics and errors
   • Gradual traffic increase
   • Data-driven deployment decisions
""")

def explain_nginx_configuration():
    """Explain Nginx reverse proxy configuration."""
    print("""
🌐 Nginx Reverse Proxy Configuration:

🔧 Core Nginx Concepts for ML APIs:

1. 📡 Reverse Proxy Setup:
   ```nginx
   # /etc/nginx/sites-available/thai-model-api
   upstream thai_api {
       # Load balancing with health checks
       server 127.0.0.1:8000 weight=3 max_fails=3 fail_timeout=30s;
       server 127.0.0.1:8001 weight=3 max_fails=3 fail_timeout=30s;
       server 127.0.0.1:8002 weight=2 max_fails=3 fail_timeout=30s;
       
       # Backup server
       server 127.0.0.1:8003 backup;
   }
   
   server {
       listen 80;
       server_name api.thai-model.com;
       
       # Redirect HTTP to HTTPS
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl http2;
       server_name api.thai-model.com;
       
       # SSL Configuration
       ssl_certificate /etc/letsencrypt/live/api.thai-model.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/api.thai-model.com/privkey.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
       
       # Security Headers
       add_header X-Frame-Options "SAMEORIGIN" always;
       add_header X-Content-Type-Options "nosniff" always;
       add_header X-XSS-Protection "1; mode=block" always;
       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
       
       # Rate Limiting
       limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
       limit_req zone=api burst=20 nodelay;
       
       # API Routes
       location /v1/ {
           proxy_pass http://thai_api;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # Timeouts for ML inference
           proxy_connect_timeout 60s;
           proxy_send_timeout 300s;
           proxy_read_timeout 300s;
           
           # Buffer settings for streaming
           proxy_buffering off;
           proxy_cache off;
       }
       
       # Health check endpoint (no rate limiting)
       location /health {
           proxy_pass http://thai_api;
           access_log off;
       }
       
       # Static files (documentation)
       location /docs/ {
           proxy_pass http://thai_api;
           
           # Enable caching for static assets
           proxy_cache_valid 200 1h;
           add_header X-Cache-Status $upstream_cache_status;
       }
   }
   ```

2. 🚀 Performance Optimizations:
   ```nginx
   # Global nginx.conf optimizations
   worker_processes auto;
   worker_connections 1024;
   
   # Enable gzip compression
   gzip on;
   gzip_vary on;
   gzip_min_length 1024;
   gzip_types
       text/plain
       text/css
       text/xml
       text/javascript
       application/json
       application/javascript
       application/xml+rss
       application/atom+xml
       image/svg+xml;
   
   # Connection keep-alive
   keepalive_timeout 65;
   keepalive_requests 100;
   
   # Buffer sizes
   client_body_buffer_size 128k;
   client_max_body_size 10m;
   client_header_buffer_size 1k;
   large_client_header_buffers 4 4k;
   ```

3. 📊 Logging and Monitoring:
   ```nginx
   # Custom log format for ML API
   log_format api_log '$remote_addr - $remote_user [$time_local] '
                      '"$request" $status $bytes_sent '
                      '"$http_referer" "$http_user_agent" '
                      'rt=$request_time uct="$upstream_connect_time" '
                      'uht="$upstream_header_time" urt="$upstream_response_time"';
   
   access_log /var/log/nginx/thai-api-access.log api_log;
   error_log /var/log/nginx/thai-api-error.log warn;
   ```

🎯 Advanced Nginx Features:
   • SSL certificate automation with Let's Encrypt
   • Geographic blocking and allow-lists
   • Request/response modification with Lua scripts
   • A/B testing with traffic splitting
   • Custom error pages and maintenance modes
""")

def explain_systemd_service_management():
    """Explain systemd service management."""
    print("""
⚙️ Systemd Service Management:

🔧 Production Service Configuration:

1. 🚀 Thai Model API Service:
   ```ini
   # /etc/systemd/system/thai-model-api.service
   [Unit]
   Description=Thai Language Model API Server
   Documentation=https://github.com/your-org/thai-model
   After=network.target redis.service postgresql.service
   Wants=redis.service
   Requires=network.target
   
   [Service]
   Type=notify
   User=thai-api
   Group=thai-api
   
   # Working directory
   WorkingDirectory=/opt/thai-model
   
   # Environment
   Environment=PYTHONPATH=/opt/thai-model
   Environment=LOG_LEVEL=info
   Environment=WORKERS=4
   EnvironmentFile=-/etc/thai-model/environment
   
   # Security settings
   NoNewPrivileges=yes
   ProtectSystem=strict
   ProtectHome=yes
   ReadWritePaths=/opt/thai-model/logs /tmp
   PrivateTmp=yes
   
   # Resource limits
   LimitNOFILE=65536
   LimitNPROC=4096
   
   # Execution
   ExecStartPre=/opt/thai-model/scripts/pre-start.sh
   ExecStart=/opt/thai-model/venv/bin/gunicorn thai_model.api.fastapi_server:app \\
             --config /etc/thai-model/gunicorn.conf.py
   ExecReload=/bin/kill -s HUP $MAINPID
   ExecStop=/bin/kill -s TERM $MAINPID
   
   # Restart policy
   Restart=always
   RestartSec=10
   StartLimitIntervalSec=60
   StartLimitBurst=3
   
   # Logging
   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=thai-api
   
   [Install]
   WantedBy=multi-user.target
   ```

2. 🔄 Multi-Instance Setup:
   ```ini
   # /etc/systemd/system/thai-model-api@.service
   [Unit]
   Description=Thai Model API Server Instance %i
   After=network.target
   
   [Service]
   Type=simple
   User=thai-api
   WorkingDirectory=/opt/thai-model
   
   # Instance-specific port
   Environment=PORT=800%i
   Environment=INSTANCE_ID=%i
   
   ExecStart=/opt/thai-model/venv/bin/uvicorn thai_model.api.fastapi_server:app \\
             --host 0.0.0.0 --port 800%i --workers 1
   
   Restart=always
   RestartSec=5
   
   [Install]
   WantedBy=multi-user.target
   ```

3. 🎯 Service Management Commands:
   ```bash
   # Enable and start service
   sudo systemctl enable thai-model-api.service
   sudo systemctl start thai-model-api.service
   
   # Check status
   sudo systemctl status thai-model-api.service
   
   # View logs
   sudo journalctl -u thai-model-api.service -f
   
   # Reload configuration
   sudo systemctl daemon-reload
   sudo systemctl reload thai-model-api.service
   
   # Multiple instances
   sudo systemctl enable thai-model-api@{0..2}.service
   sudo systemctl start thai-model-api@{0..2}.service
   ```

🛡️ Security Hardening:
   ```ini
   # Additional security options
   [Service]
   # Network isolation
   PrivateNetwork=no
   RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
   
   # Filesystem isolation
   ProtectKernelTunables=yes
   ProtectKernelModules=yes
   ProtectControlGroups=yes
   
   # System call filtering
   SystemCallFilter=@system-service
   SystemCallErrorNumber=EPERM
   
   # Capability restrictions
   CapabilityBoundingSet=CAP_NET_BIND_SERVICE
   AmbientCapabilities=CAP_NET_BIND_SERVICE
   ```
""")

def explain_infrastructure_as_code():
    """Explain Infrastructure as Code approaches."""
    print("""
📋 Infrastructure as Code (IaC):

🏗️ Terraform Configuration Example:

1. 🌐 AWS Infrastructure:
   ```hcl
   # main.tf
   provider "aws" {
     region = var.aws_region
   }
   
   # VPC and Networking
   resource "aws_vpc" "thai_model_vpc" {
     cidr_block           = "10.0.0.0/16"
     enable_dns_hostnames = true
     enable_dns_support   = true
     
     tags = {
       Name        = "thai-model-vpc"
       Environment = var.environment
     }
   }
   
   resource "aws_subnet" "public" {
     count = 2
     
     vpc_id                  = aws_vpc.thai_model_vpc.id
     cidr_block              = "10.0.${count.index + 1}.0/24"
     availability_zone       = data.aws_availability_zones.available.names[count.index]
     map_public_ip_on_launch = true
     
     tags = {
       Name = "public-subnet-${count.index + 1}"
       Type = "public"
     }
   }
   
   # Application Load Balancer
   resource "aws_lb" "thai_model_alb" {
     name               = "thai-model-alb"
     internal           = false
     load_balancer_type = "application"
     security_groups    = [aws_security_group.alb.id]
     subnets           = aws_subnet.public[*].id
     
     enable_deletion_protection = var.environment == "production"
   }
   
   # ECS Cluster for containerized deployment
   resource "aws_ecs_cluster" "thai_model_cluster" {
     name = "thai-model-cluster"
     
     setting {
       name  = "containerInsights"
       value = "enabled"
     }
   }
   
   # ECS Task Definition
   resource "aws_ecs_task_definition" "thai_model_task" {
     family                   = "thai-model-api"
     network_mode             = "awsvpc"
     requires_compatibilities = ["FARGATE"]
     cpu                      = "2048"
     memory                   = "4096"
     execution_role_arn       = aws_iam_role.ecs_execution_role.arn
     task_role_arn           = aws_iam_role.ecs_task_role.arn
     
     container_definitions = jsonencode([
       {
         name  = "thai-model-api"
         image = "${var.ecr_repository_url}:${var.image_tag}"
         
         portMappings = [{
           containerPort = 8000
           protocol      = "tcp"
         }]
         
         environment = [
           {
             name  = "LOG_LEVEL"
             value = "info"
           },
           {
             name  = "WORKERS"
             value = "4"
           }
         ]
         
         logConfiguration = {
           logDriver = "awslogs"
           options = {
             "awslogs-group"         = aws_cloudwatch_log_group.thai_model_logs.name
             "awslogs-region"        = var.aws_region
             "awslogs-stream-prefix" = "ecs"
           }
         }
         
         healthCheck = {
           command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
           interval    = 30
           timeout     = 5
           retries     = 3
           startPeriod = 60
         }
       }
     ])
   }
   ```

2. ☸️ Kubernetes with Helm:
   ```yaml
   # helm/thai-model/values.yaml
   replicaCount: 3
   
   image:
     repository: your-registry/thai-model
     tag: "latest"
     pullPolicy: IfNotPresent
   
   service:
     type: ClusterIP
     port: 80
     targetPort: 8000
   
   ingress:
     enabled: true
     className: "nginx"
     annotations:
       cert-manager.io/cluster-issuer: "letsencrypt-prod"
       nginx.ingress.kubernetes.io/rate-limit: "100"
     hosts:
       - host: api.thai-model.com
         paths:
           - path: /
             pathType: Prefix
     tls:
       - secretName: thai-model-tls
         hosts:
           - api.thai-model.com
   
   resources:
     limits:
       cpu: 2000m
       memory: 4Gi
     requests:
       cpu: 1000m
       memory: 2Gi
   
   autoscaling:
     enabled: true
     minReplicas: 3
     maxReplicas: 10
     targetCPUUtilizationPercentage: 70
     targetMemoryUtilizationPercentage: 80
   
   # Helm template: templates/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: {{ include "thai-model.fullname" . }}
     labels:
       {{- include "thai-model.labels" . | nindent 4 }}
   spec:
     replicas: {{ .Values.replicaCount }}
     selector:
       matchLabels:
         {{- include "thai-model.selectorLabels" . | nindent 6 }}
     template:
       metadata:
         labels:
           {{- include "thai-model.selectorLabels" . | nindent 8 }}
       spec:
         containers:
         - name: {{ .Chart.Name }}
           image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
           imagePullPolicy: {{ .Values.image.pullPolicy }}
           ports:
           - name: http
             containerPort: 8000
             protocol: TCP
           livenessProbe:
             httpGet:
               path: /health
               port: http
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /ready
               port: http
             initialDelaySeconds: 5
             periodSeconds: 5
           resources:
             {{- toYaml .Values.resources | nindent 12 }}
   ```

🎯 IaC Best Practices:
   • Version control all infrastructure code
   • Use modules for reusable components
   • Implement proper state management
   • Separate environments (dev/staging/prod)
   • Automated testing for infrastructure changes
""")

def explain_cicd_pipelines():
    """Explain CI/CD pipeline implementation."""
    print("""
🚀 CI/CD Pipelines for ML APIs:

🔄 GitHub Actions Workflow:

```yaml
# .github/workflows/deploy.yml
name: Deploy Thai Model API

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov
        
    - name: Run tests
      run: |
        pytest tests/ --cov=thai_model --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          
    - name: Build and push
      id: build
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./deployment/docker/Dockerfile.cpu
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: [test, build]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Update Kubernetes deployment
        kubectl set image deployment/thai-model-api \\
          thai-model-api=${{ needs.build.outputs.image-tag }} \\
          --namespace=staging
          
    - name: Verify deployment
      run: |
        kubectl rollout status deployment/thai-model-api --namespace=staging
        kubectl get pods --namespace=staging

  integration-tests:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run integration tests
      run: |
        python tests/integration/test_api_endpoints.py \\
          --base-url=https://staging-api.thai-model.com

  deploy-production:
    needs: [integration-tests]
    if: github.ref == 'refs/heads/main' && success()
    runs-on: ubuntu-latest
    environment: production
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # Blue-green deployment strategy
        ./scripts/blue-green-deploy.sh ${{ needs.build.outputs.image-tag }}
        
    - name: Post-deployment tests
      run: |
        python tests/smoke/test_production.py
```

🎯 Pipeline Stages Explained:

1. 🧪 **Test Stage**:
   • Unit tests with coverage reporting
   • Code quality checks (linting, formatting)
   • Security vulnerability scanning
   • Model validation tests

2. 🏗️ **Build Stage**:
   • Docker image building with multi-stage optimization
   • Image scanning for vulnerabilities
   • Push to container registry with proper tagging
   • Artifact generation and storage

3. 🚀 **Deploy Staging**:
   • Automated deployment to staging environment
   • Database migrations and configuration updates
   • Health checks and smoke tests
   • Performance baseline validation

4. ✅ **Integration Tests**:
   • End-to-end API testing
   • Load testing and performance validation
   • Cross-service integration verification
   • User acceptance test automation

5. 🏭 **Deploy Production**:
   • Blue-green or canary deployment strategy
   • Traffic routing and gradual rollout
   • Monitoring and alerting activation
   • Rollback capabilities and procedures
""")

def main():
    print_header("Module 4.2: Production Deployment")
    
    # Step 1: Production Architecture
    print_step(1, "Production Architecture & Design Patterns")
    explain_production_architecture()
    
    input("\n🔍 Press Enter to learn about Nginx configuration...")
    
    # Step 2: Nginx Configuration
    print_step(2, "Nginx Reverse Proxy Configuration")
    explain_nginx_configuration()
    
    input("\n🔍 Press Enter to learn about systemd services...")
    
    # Step 3: Systemd Service Management
    print_step(3, "Systemd Service Management")
    explain_systemd_service_management()
    
    input("\n🔍 Press Enter to learn about Infrastructure as Code...")
    
    # Step 4: Infrastructure as Code
    print_step(4, "Infrastructure as Code (IaC)")
    explain_infrastructure_as_code()
    
    input("\n🔍 Press Enter to learn about CI/CD pipelines...")
    
    # Step 5: CI/CD Pipelines
    print_step(5, "CI/CD Pipeline Implementation")
    explain_cicd_pipelines()
    
    input("\n🔍 Press Enter to see practical exercises...")
    
    # Step 6: Practical Exercises
    print_step(6, "Production Deployment Exercises")
    
    print("""
🧪 Production Deployment Hands-on Exercises:

1. 🌐 Configure Nginx Reverse Proxy:
   ```bash
   # Examine the existing Nginx configuration
   cat /home/chanthaphan/project/deployment/nginx/thai-model-api.nginx
   
   # Test Nginx configuration
   sudo nginx -t
   
   # Enable the site (if you have Nginx installed)
   sudo ln -s /home/chanthaphan/project/deployment/nginx/thai-model-api.nginx \\
              /etc/nginx/sites-available/thai-model-api
   
   # Test upstream health checking
   curl -H "Host: api.thai-model.com" http://localhost/health
   ```

2. ⚙️ Setup Systemd Service:
   ```bash
   # Examine the systemd service file
   cat /home/chanthaphan/project/deployment/systemd/thai-model-api.service
   
   # Install the service (requires sudo)
   sudo cp /home/chanthaphan/project/deployment/systemd/thai-model-api.service \\
           /etc/systemd/system/
   
   # Reload systemd and enable service
   sudo systemctl daemon-reload
   sudo systemctl enable thai-model-api.service
   
   # Check service status
   sudo systemctl status thai-model-api.service
   
   # View service logs
   sudo journalctl -u thai-model-api.service -f
   ```

3. 🐳 Production Docker Setup:
   ```bash
   cd /home/chanthaphan/project/deployment/docker
   
   # Build production-ready image
   docker build -f Dockerfile.cpu -t thai-model:production \\
     --target production .
   
   # Run with production settings
   docker run -d \\
     --name thai-model-prod \\
     -p 8000:8000 \\
     -e WORKERS=4 \\
     -e LOG_LEVEL=info \\
     --restart unless-stopped \\
     --health-cmd="curl -f http://localhost:8000/health || exit 1" \\
     --health-interval=30s \\
     thai-model:production
   
   # Check container health
   docker ps --filter name=thai-model-prod
   docker logs thai-model-prod
   ```

4. 📊 Multi-Service Stack with Compose:
   ```bash
   # Start production stack
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   
   # Verify all services
   docker-compose ps
   
   # Check service logs
   docker-compose logs -f thai-api nginx redis
   
   # Scale the API service
   docker-compose up --scale thai-api=3 -d
   
   # Test load balancing
   for i in {1..10}; do
     curl -H "Host: api.thai-model.com" http://localhost/health
   done
   ```

5. 🔍 Health Monitoring Setup:
   ```bash
   # Create health check script
   cat > health_check.sh << 'EOF'
   #!/bin/bash
   
   # Health check endpoints
   ENDPOINTS=(
     "http://localhost:8000/health"
     "http://localhost:8000/ready"
     "http://localhost:8000/v1/models"
   )
   
   for endpoint in "${ENDPOINTS[@]}"; do
     echo "Checking $endpoint..."
     response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint")
     if [ "$response" == "200" ]; then
       echo "✅ $endpoint is healthy"
     else
       echo "❌ $endpoint returned $response"
     fi
   done
   EOF
   
   chmod +x health_check.sh
   ./health_check.sh
   ```

6. 📈 Load Testing:
   ```bash
   # Install Apache Bench (if not available)
   # sudo apt-get install apache2-utils
   
   # Simple load test
   ab -n 1000 -c 10 http://localhost:8000/health
   
   # Test API endpoint with POST
   ab -n 100 -c 5 -p request.json -T application/json \\
      http://localhost:8000/v1/chat/completions
   
   # Create request.json for testing
   cat > request.json << 'EOF'
   {
     "model": "thai-model",
     "messages": [{"role": "user", "content": "สวัสดี"}],
     "max_tokens": 50
   }
   EOF
   ```

7. 🎯 Blue-Green Deployment Simulation:
   ```bash
   # Blue-Green deployment script
   cat > blue_green_deploy.sh << 'EOF'
   #!/bin/bash
   
   NEW_IMAGE=$1
   CURRENT_COLOR=$(docker ps --filter "name=thai-model" --format "{{.Names}}" | head -1 | cut -d'-' -f3)
   
   if [ "$CURRENT_COLOR" == "blue" ]; then
     NEW_COLOR="green"
   else
     NEW_COLOR="blue"
   fi
   
   echo "Deploying $NEW_IMAGE to $NEW_COLOR environment..."
   
   # Start new environment
   docker run -d --name "thai-model-$NEW_COLOR" \\
     -p 8001:8000 \\
     "$NEW_IMAGE"
   
   # Health check new environment
   sleep 10
   if curl -f http://localhost:8001/health; then
     echo "✅ New environment is healthy"
     
     # Switch traffic (update nginx upstream)
     echo "🔄 Switching traffic to $NEW_COLOR"
     
     # Stop old environment
     OLD_CONTAINER="thai-model-$CURRENT_COLOR"
     if docker ps -q -f name="$OLD_CONTAINER"; then
       docker stop "$OLD_CONTAINER"
       docker rm "$OLD_CONTAINER"
     fi
     
     echo "✅ Deployment complete"
   else
     echo "❌ New environment failed health check, rolling back"
     docker stop "thai-model-$NEW_COLOR"
     docker rm "thai-model-$NEW_COLOR"
   fi
   EOF
   
   chmod +x blue_green_deploy.sh
   ```

8. 🔐 SSL/TLS Setup with Let's Encrypt:
   ```bash
   # Install certbot (if available)
   # sudo apt-get install certbot python3-certbot-nginx
   
   # Generate SSL certificate
   # sudo certbot --nginx -d api.thai-model.com
   
   # Test SSL configuration
   # sudo nginx -t
   # sudo systemctl reload nginx
   
   # Verify SSL setup
   # curl -I https://api.thai-model.com/health
   ```

🎯 Production Deployment Checklist:

📋 **Pre-Deployment**:
   ✅ Load testing completed
   ✅ Security scanning passed
   ✅ Backup and rollback plan ready
   ✅ Monitoring and alerting configured
   ✅ Database migrations tested
   ✅ SSL certificates valid

🚀 **Deployment Process**:
   ✅ Blue-green or canary strategy
   ✅ Health checks at each stage  
   ✅ Performance validation
   ✅ Error rate monitoring
   ✅ Rollback triggers defined
   ✅ Communication plan executed

📊 **Post-Deployment**:
   ✅ Service health monitoring
   ✅ Performance metrics collection
   ✅ Error tracking and alerting
   ✅ User feedback monitoring
   ✅ Capacity planning updates
   ✅ Documentation updates

🎯 Key Takeaways:
   • Production deployment requires multiple layers of redundancy
   • Nginx provides powerful reverse proxy and load balancing
   • Systemd ensures reliable service management and recovery
   • Infrastructure as Code enables repeatable deployments
   • CI/CD pipelines automate testing and deployment processes

🚀 Ready for Module 5.1: Performance Optimization!
""")

if __name__ == "__main__":
    main()
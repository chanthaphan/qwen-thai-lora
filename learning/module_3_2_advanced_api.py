#!/usr/bin/env python3
"""
Module 3.2: Advanced API Features
===============================

Interactive learning script for advanced FastAPI features including streaming,
authentication, rate limiting, and production deployment techniques.
"""

import sys
import json
import time
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

def explain_streaming_responses():
    """Explain streaming responses in detail."""
    print("""
📹 Streaming Responses Deep Dive:

🌊 Why Streaming?
   • Real-time token generation for LLMs
   • Better user experience (progressive display)
   • Lower perceived latency
   • Handles long-running generations
   • Memory efficient for large responses

🔧 Implementation Patterns:

1. 📡 Server-Sent Events (SSE):
   ```python
   from fastapi.responses import StreamingResponse
   import json
   
   async def generate_stream(prompt: str):
       async for token in model.generate_streaming(prompt):
           # SSE format: "data: {json}\\n\\n"
           yield f"data: {json.dumps({'token': token, 'done': False})}\\n\\n"
       
       # Send completion signal
       yield f"data: {json.dumps({'done': True})}\\n\\n"
   
   @app.post("/v1/stream")
   async def stream_generation(request: GenerateRequest):
       return StreamingResponse(
           generate_stream(request.prompt),
           media_type="text/event-stream",
           headers={
               "Cache-Control": "no-cache",
               "Connection": "keep-alive",
               "X-Accel-Buffering": "no"  # Disable nginx buffering
           }
       )
   ```

2. 🚰 Chunked Transfer Encoding:
   ```python
   async def stream_chunks(text_generator):
       async for chunk in text_generator:
           # Send raw text chunks
           yield chunk.encode('utf-8')
   
   @app.post("/stream-raw")
   async def stream_raw_text(prompt: str):
       return StreamingResponse(
           stream_chunks(model.generate_streaming(prompt)),
           media_type="text/plain"
       )
   ```

3. 🔄 WebSocket Streaming:
   ```python
   from fastapi import WebSocket
   
   @app.websocket("/ws/generate")
   async def websocket_generate(websocket: WebSocket):
       await websocket.accept()
       
       try:
           while True:
               # Receive prompt
               data = await websocket.receive_json()
               prompt = data.get("prompt")
               
               # Stream response
               async for token in model.generate_streaming(prompt):
                   await websocket.send_json({
                       "type": "token",
                       "content": token
                   })
               
               # Send completion
               await websocket.send_json({
                   "type": "complete",
                   "content": ""
               })
               
       except Exception as e:
           await websocket.send_json({
               "type": "error", 
               "content": str(e)
           })
   ```

🎯 Streaming Best Practices:
   • Always set proper headers (Cache-Control, Connection)
   • Handle client disconnections gracefully
   • Implement backpressure for slow clients
   • Use JSON format for structured streaming
   • Add heartbeat for long-running streams
""")

def explain_authentication_security():
    """Explain authentication and security features."""
    print("""
🔐 Authentication & Security Systems:

🎫 Multi-Layer Security Approach:

1. 🔑 API Key Authentication:
   ```python
   from fastapi import HTTPException, Depends, Security
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   import hashlib
   import secrets
   
   class APIKeyAuth:
       def __init__(self):
           self.valid_keys = self.load_api_keys()
           self.bearer = HTTPBearer(auto_error=False)
       
       def load_api_keys(self):
           # In production: load from secure database
           return {
               "sk-1234567890abcdef": {"name": "admin", "rate_limit": 1000},
               "sk-0987654321fedcba": {"name": "user", "rate_limit": 100}
           }
       
       async def __call__(self, credentials: HTTPAuthorizationCredentials = Security(self.bearer)):
           if not credentials:
               raise HTTPException(401, "API key required")
           
           token = credentials.credentials
           if token not in self.valid_keys:
               raise HTTPException(401, "Invalid API key")
           
           return self.valid_keys[token]
   
   # Usage
   api_key_auth = APIKeyAuth()
   
   @app.post("/protected/generate")
   async def protected_generate(
       request: GenerateRequest,
       user_info: dict = Depends(api_key_auth)
   ):
       # user_info contains key metadata
       return await generate_text(request.prompt)
   ```

2. 🔐 JWT Token Authentication:
   ```python
   from jose import JWTError, jwt
   from datetime import datetime, timedelta
   
   class JWTAuth:
       def __init__(self, secret_key: str):
           self.secret_key = secret_key
           self.algorithm = "HS256"
       
       def create_token(self, user_id: str, expires_delta: timedelta = None):
           if expires_delta:
               expire = datetime.utcnow() + expires_delta
           else:
               expire = datetime.utcnow() + timedelta(minutes=15)
           
           payload = {
               "sub": user_id,
               "exp": expire,
               "iat": datetime.utcnow(),
               "type": "access"
           }
           
           return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
       
       def verify_token(self, token: str):
           try:
               payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
               user_id = payload.get("sub")
               if user_id is None:
                   raise HTTPException(401, "Invalid token")
               return user_id
           except JWTError:
               raise HTTPException(401, "Token validation failed")
   ```

3. 🛡️ Role-Based Access Control (RBAC):
   ```python
   from enum import Enum
   from functools import wraps
   
   class UserRole(str, Enum):
       ADMIN = "admin"
       USER = "user"
       READONLY = "readonly"
   
   class Permission(str, Enum):
       READ_MODELS = "read:models"
       GENERATE_TEXT = "generate:text"
       ADMIN_PANEL = "admin:panel"
   
   ROLE_PERMISSIONS = {
       UserRole.ADMIN: [Permission.READ_MODELS, Permission.GENERATE_TEXT, Permission.ADMIN_PANEL],
       UserRole.USER: [Permission.READ_MODELS, Permission.GENERATE_TEXT],
       UserRole.READONLY: [Permission.READ_MODELS]
   }
   
   def require_permission(permission: Permission):
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               user_info = kwargs.get('current_user')
               if not user_info:
                   raise HTTPException(401, "Authentication required")
               
               user_role = user_info.get('role')
               if permission not in ROLE_PERMISSIONS.get(user_role, []):
                   raise HTTPException(403, "Insufficient permissions")
               
               return await func(*args, **kwargs)
           return wrapper
       return decorator
   ```

🔒 Security Headers & HTTPS:
   ```python
   from fastapi.middleware.trustedhost import TrustedHostMiddleware
   from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
   
   # Force HTTPS in production
   app.add_middleware(HTTPSRedirectMiddleware)
   
   # Restrict allowed hosts
   app.add_middleware(
       TrustedHostMiddleware, 
       allowed_hosts=["api.myapp.com", "localhost"]
   )
   
   # Security headers
   @app.middleware("http")
   async def add_security_headers(request: Request, call_next):
       response = await call_next(request)
       response.headers["X-Content-Type-Options"] = "nosniff"
       response.headers["X-Frame-Options"] = "DENY"
       response.headers["X-XSS-Protection"] = "1; mode=block"
       response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
       return response
   ```
""")

def explain_rate_limiting():
    """Explain rate limiting implementation."""
    print("""
⏱️ Advanced Rate Limiting:

🎯 Multi-Tier Rate Limiting Strategy:

1. 📊 Token Bucket Algorithm:
   ```python
   import time
   import asyncio
   from collections import defaultdict
   
   class TokenBucket:
       def __init__(self, capacity: int, refill_rate: float):
           self.capacity = capacity
           self.tokens = capacity
           self.refill_rate = refill_rate  # tokens per second
           self.last_refill = time.time()
       
       def consume(self, tokens: int = 1) -> bool:
           self._refill()
           if self.tokens >= tokens:
               self.tokens -= tokens
               return True
           return False
       
       def _refill(self):
           now = time.time()
           elapsed = now - self.last_refill
           self.tokens = min(
               self.capacity,
               self.tokens + elapsed * self.refill_rate
           )
           self.last_refill = now
   
   class RateLimiter:
       def __init__(self):
           self.buckets = defaultdict(lambda: TokenBucket(100, 1.0))  # 100 tokens, 1/sec refill
       
       def is_allowed(self, key: str, cost: int = 1) -> bool:
           return self.buckets[key].consume(cost)
   ```

2. 🏷️ Tiered Rate Limiting:
   ```python
   from enum import Enum
   
   class RateLimitTier(Enum):
       FREE = {"requests_per_minute": 10, "tokens_per_day": 1000}
       BASIC = {"requests_per_minute": 100, "tokens_per_day": 10000}
       PREMIUM = {"requests_per_minute": 1000, "tokens_per_day": 100000}
       ENTERPRISE = {"requests_per_minute": 10000, "tokens_per_day": 1000000}
   
   class TieredRateLimiter:
       def __init__(self):
           self.request_buckets = defaultdict(dict)
           self.token_buckets = defaultdict(dict)
       
       def check_limits(self, user_id: str, tier: RateLimitTier, tokens_requested: int):
           # Check request rate limit
           if not self._check_request_limit(user_id, tier):
               raise HTTPException(429, "Request rate limit exceeded")
           
           # Check token usage limit
           if not self._check_token_limit(user_id, tier, tokens_requested):
               raise HTTPException(429, "Token limit exceeded")
           
           return True
       
       def _check_request_limit(self, user_id: str, tier: RateLimitTier):
           if user_id not in self.request_buckets:
               self.request_buckets[user_id] = TokenBucket(
                   capacity=tier.value["requests_per_minute"],
                   refill_rate=tier.value["requests_per_minute"] / 60  # per second
               )
           
           return self.request_buckets[user_id].consume(1)
   ```

3. 🌍 Distributed Rate Limiting (Redis):
   ```python
   import redis
   import time
   
   class DistributedRateLimiter:
       def __init__(self, redis_client: redis.Redis):
           self.redis = redis_client
       
       async def is_allowed(self, key: str, limit: int, window: int) -> bool:
           \"\"\"
           Sliding window rate limiter using Redis
           key: identifier (user_id, ip_address, etc.)
           limit: max requests per window
           window: time window in seconds
           \"\"\"
           now = time.time()
           pipeline = self.redis.pipeline()
           
           # Remove old entries outside the window
           pipeline.zremrangebyscore(key, 0, now - window)
           
           # Count current entries in window
           pipeline.zcard(key)
           
           # Add current request
           pipeline.zadd(key, {str(now): now})
           
           # Set expiration
           pipeline.expire(key, window)
           
           results = await pipeline.execute()
           request_count = results[1]
           
           return request_count < limit
   ```

💡 Rate Limiting Best Practices:
   • Use different limits for different endpoints
   • Implement graceful degradation
   • Provide clear rate limit headers
   • Consider burst allowances for legitimate traffic
   • Monitor and alert on rate limit violations
""")

def explain_error_handling():
    """Explain comprehensive error handling."""
    print("""
❌ Production Error Handling:

🛡️ Structured Error Response System:

1. 📋 Custom Exception Classes:
   ```python
   from fastapi import HTTPException
   from typing import Optional, Dict, Any
   
   class APIError(HTTPException):
       def __init__(
           self,
           status_code: int,
           message: str,
           error_code: str,
           details: Optional[Dict[str, Any]] = None
       ):
           self.error_code = error_code
           self.details = details or {}
           super().__init__(status_code=status_code, detail=message)
   
   class ModelError(APIError):
       def __init__(self, message: str, details: Dict = None):
           super().__init__(
               status_code=500,
               message=message,
               error_code="MODEL_ERROR",
               details=details
           )
   
   class ValidationError(APIError):
       def __init__(self, message: str, field: str = None):
           super().__init__(
               status_code=422,
               message=message,
               error_code="VALIDATION_ERROR",
               details={"field": field} if field else {}
           )
   ```

2. 🎯 Global Exception Handler:
   ```python
   from fastapi import Request
   from fastapi.responses import JSONResponse
   import logging
   import traceback
   import uuid
   
   logger = logging.getLogger(__name__)
   
   @app.exception_handler(APIError)
   async def api_error_handler(request: Request, exc: APIError):
       error_id = str(uuid.uuid4())
       
       # Log error details
       logger.error(
           f"API Error {error_id}: {exc.error_code} - {exc.detail}",
           extra={
               "error_id": error_id,
               "error_code": exc.error_code,
               "request_path": request.url.path,
               "details": exc.details
           }
       )
       
       return JSONResponse(
           status_code=exc.status_code,
           content={
               "error": {
                   "code": exc.error_code,
                   "message": exc.detail,
                   "error_id": error_id,
                   "details": exc.details
               }
           }
       )
   
   @app.exception_handler(Exception)
   async def general_exception_handler(request: Request, exc: Exception):
       error_id = str(uuid.uuid4())
       
       # Log full traceback for unexpected errors
       logger.error(
           f"Unexpected error {error_id}: {str(exc)}",
           exc_info=True,
           extra={
               "error_id": error_id,
               "request_path": request.url.path,
               "traceback": traceback.format_exc()
           }
       )
       
       return JSONResponse(
           status_code=500,
           content={
               "error": {
                   "code": "INTERNAL_ERROR",
                   "message": "An unexpected error occurred",
                   "error_id": error_id
               }
           }
       )
   ```

3. 🔍 Request Context & Tracing:
   ```python
   import contextvars
   from uuid import uuid4
   
   # Context variable for request tracing
   request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('request_id')
   
   @app.middleware("http")
   async def add_request_id(request: Request, call_next):
       request_id = str(uuid4())
       request_id_var.set(request_id)
       
       # Add to response headers
       response = await call_next(request)
       response.headers["X-Request-ID"] = request_id
       
       return response
   
   # Usage in error logging
   def log_with_context(message: str, level: str = "info"):
       try:
           request_id = request_id_var.get()
       except LookupError:
           request_id = "unknown"
       
       logger.log(
           getattr(logging, level.upper()),
           f"[{request_id}] {message}"
       )
   ```

📊 Error Monitoring Integration:
   ```python
   # Sentry integration for error tracking
   import sentry_sdk
   from sentry_sdk.integrations.fastapi import FastApiIntegration
   
   sentry_sdk.init(
       dsn="your-sentry-dsn",
       integrations=[FastApiIntegration()],
       traces_sample_rate=0.1,
       environment="production"
   )
   
   # Custom error reporting
   def report_error(error: Exception, context: Dict[str, Any]):
       with sentry_sdk.push_scope() as scope:
           for key, value in context.items():
               scope.set_extra(key, value)
           sentry_sdk.capture_exception(error)
   ```
""")

def explain_production_deployment():
    """Explain production deployment considerations."""
    print("""
🏭 Production Deployment Strategies:

🚀 Multi-Process Deployment:

1. 🔧 Gunicorn + Uvicorn Workers:
   ```bash
   # gunicorn_config.py
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "uvicorn.workers.UvicornWorker"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 50
   preload_app = True
   timeout = 120
   keepalive = 2
   
   # Start command
   gunicorn thai_model.api.fastapi_server:app -c gunicorn_config.py
   ```

2. 🐳 Docker Production Setup:
   ```dockerfile
   # Multi-stage production Dockerfile
   FROM python:3.11-slim as base
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \\
       gcc g++ make \\
       && rm -rf /var/lib/apt/lists/*
   
   # Production stage
   FROM base as production
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   RUN pip install --no-cache-dir -e .
   
   # Non-root user
   RUN useradd --create-home --shell /bin/bash app
   USER app
   
   EXPOSE 8000
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
       CMD curl -f http://localhost:8000/health || exit 1
   
   CMD ["gunicorn", "thai_model.api.fastapi_server:app", "-c", "gunicorn_config.py"]
   ```

3. ☸️ Kubernetes Deployment:
   ```yaml
   # k8s-deployment.yaml
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
         - name: api
           image: thai-model:latest
           ports:
           - containerPort: 8000
           resources:
             requests:
               memory: "2Gi"
               cpu: "500m"
             limits:
               memory: "4Gi"  
               cpu: "2000m"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /ready
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
   ```

🔍 Monitoring & Observability:

1. 📊 Metrics Collection:
   ```python
   from prometheus_client import Counter, Histogram, generate_latest
   
   # Metrics
   REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
   REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
   MODEL_INFERENCE_TIME = Histogram('model_inference_duration_seconds', 'Model inference time')
   
   @app.middleware("http")
   async def metrics_middleware(request: Request, call_next):
       start_time = time.time()
       
       response = await call_next(request)
       
       duration = time.time() - start_time
       REQUEST_COUNT.labels(
           method=request.method,
           endpoint=request.url.path,
           status=response.status_code
       ).inc()
       REQUEST_DURATION.observe(duration)
       
       return response
   
   @app.get("/metrics")
   async def get_metrics():
       return Response(generate_latest(), media_type="text/plain")
   ```

2. 🏥 Health Checks:
   ```python
   from enum import Enum
   
   class HealthStatus(str, Enum):
       HEALTHY = "healthy"
       UNHEALTHY = "unhealthy"
       DEGRADED = "degraded"
   
   @app.get("/health")
   async def health_check():
       checks = {
           "model": await check_model_health(),
           "database": await check_db_health(),
           "external_apis": await check_external_services()
       }
       
       overall_status = HealthStatus.HEALTHY
       if any(status == HealthStatus.UNHEALTHY for status in checks.values()):
           overall_status = HealthStatus.UNHEALTHY
       elif any(status == HealthStatus.DEGRADED for status in checks.values()):
           overall_status = HealthStatus.DEGRADED
       
       return {
           "status": overall_status,
           "checks": checks,
           "timestamp": datetime.utcnow().isoformat()
       }
   ```

🎯 Performance Optimization:
   • Connection pooling for databases
   • Response caching with Redis
   • Model warmup and preloading
   • Batch request processing
   • Load balancing strategies
""")

def main():
    print_header("Module 3.2: Advanced API Features")
    
    # Step 1: Streaming Responses
    print_step(1, "Streaming Responses & Real-time APIs")
    explain_streaming_responses()
    
    input("\n🔍 Press Enter to learn about authentication...")
    
    # Step 2: Authentication & Security
    print_step(2, "Authentication & Security Systems")
    explain_authentication_security()
    
    input("\n🔍 Press Enter to learn about rate limiting...")
    
    # Step 3: Rate Limiting
    print_step(3, "Advanced Rate Limiting")
    explain_rate_limiting()
    
    input("\n🔍 Press Enter to learn about error handling...")
    
    # Step 4: Error Handling
    print_step(4, "Production Error Handling")
    explain_error_handling()
    
    input("\n🔍 Press Enter to learn about production deployment...")
    
    # Step 5: Production Deployment
    print_step(5, "Production Deployment Strategies")
    explain_production_deployment()
    
    input("\n🔍 Press Enter to see practical exercises...")
    
    # Step 6: Practical Exercises
    print_step(6, "Advanced API Implementation Exercises")
    
    print("""
🧪 Advanced API Feature Experiments:

1. 📹 Test Streaming Response:
   ```python
   # Create a streaming client
   import httpx
   import asyncio
   
   async def test_streaming():
       async with httpx.AsyncClient() as client:
           async with client.stream(
               'POST',
               'http://localhost:8000/v1/chat/completions',
               json={
                   "model": "thai-model",
                   "messages": [{"role": "user", "content": "เล่าเรื่องสั้น"}],
                   "stream": True
               }
           ) as response:
               async for line in response.aiter_lines():
                   if line.startswith('data: '):
                       data = line[6:]  # Remove 'data: ' prefix
                       if data != '[DONE]':
                           import json
                           chunk = json.loads(data)
                           print(chunk.get('choices', [{}])[0].get('delta', {}).get('content', ''), end='')
   
   asyncio.run(test_streaming())
   ```

2. 🔐 Implement API Key Authentication:
   ```python
   # Add to your local API testing
   import os
   
   # Set API key
   API_KEY = "sk-test123"
   
   # Test protected endpoint
   headers = {"Authorization": f"Bearer {API_KEY}"}
   response = requests.post(
       "http://localhost:8000/v1/chat/completions",
       headers=headers,
       json={"messages": [{"role": "user", "content": "สวัสดี"}]}
   )
   ```

3. ⏱️ Implement Rate Limiting:
   ```python
   # Test rate limiting behavior
   import time
   import asyncio
   
   async def test_rate_limit():
       async with httpx.AsyncClient() as client:
           # Send rapid requests
           tasks = []
           for i in range(20):  # Send 20 requests quickly
               task = client.get("http://localhost:8000/health")
               tasks.append(task)
           
           responses = await asyncio.gather(*tasks, return_exceptions=True)
           
           success_count = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
           rate_limited = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 429)
           
           print(f"Successful: {success_count}, Rate limited: {rate_limited}")
   ```

4. 📊 Monitor API Performance:
   ```python
   # Create performance monitoring script
   import time
   import statistics
   
   async def benchmark_api():
       times = []
       async with httpx.AsyncClient() as client:
           for i in range(100):
               start = time.time()
               response = await client.get("http://localhost:8000/health")
               duration = time.time() - start
               times.append(duration)
               
               if response.status_code != 200:
                   print(f"Error: {response.status_code}")
           
           print(f"Average response time: {statistics.mean(times):.3f}s")
           print(f"95th percentile: {statistics.quantiles(times, n=20)[18]:.3f}s")
           print(f"Max response time: {max(times):.3f}s")
   ```

5. 🛡️ Test Error Handling:
   ```bash
   # Test various error scenarios
   
   # Invalid JSON
   curl -X POST "http://localhost:8000/v1/chat/completions" \\
     -H "Content-Type: application/json" \\
     -d '{"invalid": json}'
   
   # Missing required fields
   curl -X POST "http://localhost:8000/v1/chat/completions" \\
     -H "Content-Type: application/json" \\
     -d '{}'
   
   # Invalid parameter values
   curl -X POST "http://localhost:8000/v1/chat/completions" \\
     -H "Content-Type: application/json" \\
     -d '{"temperature": 5.0, "messages": []}'
   ```

6. 🐳 Production Deployment Testing:
   ```bash
   # Build production Docker image
   cd /home/chanthaphan/project
   docker build -f deployment/docker/Dockerfile.cpu -t thai-model:prod .
   
   # Run with production settings
   docker run -p 8000:8000 \\
     -e WORKERS=4 \\
     -e LOG_LEVEL=info \\
     thai-model:prod
   
   # Test health endpoint
   curl http://localhost:8000/health
   
   # Load test with multiple workers
   ab -n 1000 -c 10 http://localhost:8000/health
   ```

📈 Performance Optimization Exercises:

🚀 Caching Implementation:
   ```python
   # Add Redis caching to responses
   import redis
   import json
   from functools import wraps
   
   redis_client = redis.Redis(host='localhost', port=6379, db=0)
   
   def cache_response(expiry_seconds=300):
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               # Generate cache key from function args
               cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
               
               # Try to get from cache
               cached = redis_client.get(cache_key)
               if cached:
                   return json.loads(cached)
               
               # Execute function and cache result
               result = await func(*args, **kwargs)
               redis_client.setex(cache_key, expiry_seconds, json.dumps(result))
               
               return result
           return wrapper
       return decorator
   ```

🔍 Monitoring Integration:
   ```python
   # Add comprehensive logging
   import structlog
   from pythonjsonlogger import jsonlogger
   
   # Configure structured logging
   logging.basicConfig(
       format='%(asctime)s %(name)s %(levelname)s %(message)s',
       level=logging.INFO
   )
   
   logger = structlog.get_logger()
   
   @app.middleware("http")
   async def logging_middleware(request: Request, call_next):
       start_time = time.time()
       
       logger.info(
           "Request started",
           method=request.method,
           path=request.url.path,
           client_ip=request.client.host
       )
       
       response = await call_next(request)
       
       duration = time.time() - start_time
       logger.info(
           "Request completed",
           method=request.method,
           path=request.url.path,
           status_code=response.status_code,
           duration=duration
       )
       
       return response
   ```

🎯 Key Takeaways:
   • Streaming enables real-time user experiences
   • Multi-layer security protects against various threats
   • Rate limiting prevents abuse and ensures fair usage
   • Comprehensive error handling improves debugging
   • Production deployment requires careful planning and monitoring

🚀 Ready for Module 4.1: Docker Mastery!
""")

if __name__ == "__main__":
    main()
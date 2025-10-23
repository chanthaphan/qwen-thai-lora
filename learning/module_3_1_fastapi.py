#!/usr/bin/env python3
"""
Module 3.1: FastAPI Fundamentals
===============================

Interactive learning script to master modern API development with FastAPI.
"""

import sys
import json
import asyncio
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

def explain_fastapi_basics():
    """Explain FastAPI fundamentals."""
    print("""
🚀 FastAPI Fundamentals:

🌟 Why FastAPI?
   • Extremely fast performance (on par with Node.js/Go)
   • Automatic API documentation (OpenAPI/Swagger)
   • Type hints for automatic validation
   • Built-in async/await support
   • Production-ready with security features

🏗️ Core Concepts:

1. 📋 Automatic Documentation:
   ```python
   from fastapi import FastAPI
   
   app = FastAPI(
       title="Thai Language Model API",
       description="Production-ready Thai LLM API",
       version="1.0.0"
   )
   
   @app.get("/")
   async def root():
       return {"message": "Thai Model API is running!"}
   ```

2. 🎯 Path Parameters & Query Parameters:
   ```python
   @app.get("/models/{model_id}")
   async def get_model(model_id: str, include_config: bool = False):
       return {"model_id": model_id, "config": include_config}
   ```

3. 📊 Request/Response Models with Pydantic:
   ```python
   from pydantic import BaseModel
   from typing import List, Optional
   
   class ChatMessage(BaseModel):
       role: str  # "user" or "assistant"
       content: str
   
   class ChatRequest(BaseModel):
       model: str = "thai-model"
       messages: List[ChatMessage]
       temperature: Optional[float] = 0.7
       max_tokens: Optional[int] = 512
   
   @app.post("/v1/chat/completions")
   async def chat_completion(request: ChatRequest):
       # Type validation happens automatically!
       return {"response": "Generated text..."}
   ```

4. ⚡ Async/Await for Performance:
   ```python
   import asyncio
   
   @app.post("/generate")
   async def generate_async(prompt: str):
       # Non-blocking I/O operations
       result = await model.generate_async(prompt)
       return {"generated_text": result}
   ```

🔧 Key Features:
   • Automatic request validation
   • Type conversion and coercion  
   • Error handling with HTTP status codes
   • Dependency injection system
   • Middleware support (CORS, authentication, etc.)
   • WebSocket support for real-time features
""")

def demonstrate_api_structure():
    """Demonstrate API structure from the actual code."""
    print("""
🏗️ Thai Model API Structure Analysis:
""")
    
    project_root = Path(__file__).parent.parent
    api_file = project_root / "thai_model" / "api" / "fastapi_server.py"
    models_file = project_root / "thai_model" / "api" / "models.py"
    
    # Analyze the actual API structure
    if api_file.exists():
        print(f"📄 Analyzing {api_file.name}:")
        
        with open(api_file, 'r') as f:
            content = f.read()
        
        # Extract key components
        print(f"\n🎯 Key Components Found:")
        
        components = {
            'class ThaiModelAPI': '🤖 Main API class',
            '@app.post': '📡 POST endpoints',
            '@app.get': '📡 GET endpoints',
            'async def': '⚡ Async handlers',
            'StreamingResponse': '📹 Streaming support',
            'HTTPException': '❌ Error handling'
        }
        
        for component, description in components.items():
            if component in content:
                count = content.count(component)
                print(f"  • {description}: {count} occurrences")
        
        # Show endpoints
        print(f"\n📡 API Endpoints:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '@app.' in line and ('get(' in line or 'post(' in line):
                endpoint = line.strip()
                # Get the function name from next lines
                for j in range(i+1, min(i+3, len(lines))):
                    if 'async def' in lines[j] or 'def' in lines[j]:
                        func_name = lines[j].split('def ')[1].split('(')[0]
                        print(f"  • {endpoint}")
                        print(f"    └─ Handler: {func_name}()")
                        break
    
    # Analyze Pydantic models
    if models_file.exists():
        print(f"\n📋 Analyzing {models_file.name}:")
        
        with open(models_file, 'r') as f:
            content = f.read()
        
        # Extract model classes
        lines = content.split('\n')
        models = []
        for line in lines:
            if 'class ' in line and 'BaseModel' in line:
                model_name = line.split('class ')[1].split('(')[0]
                models.append(model_name)
        
        print(f"🏷️ Pydantic Models Found:")
        for model in models:
            print(f"  • {model}")

def explain_async_programming():
    """Explain async/await programming concepts."""
    print("""
⚡ Async/Await Programming in FastAPI:

🤔 Why Async?
   • Non-blocking I/O operations
   • Handle thousands of concurrent requests
   • Better resource utilization
   • Essential for ML model inference

🔄 Sync vs Async Comparison:

1. 🐌 Synchronous (Blocking):
   ```python
   def generate_text(prompt):
       # Blocks thread for 2-5 seconds during inference
       result = model.generate(prompt)
       return result
   
   # Can only handle ~1-2 requests/second per worker
   ```

2. ⚡ Asynchronous (Non-blocking):
   ```python
   async def generate_text_async(prompt):
       # Other requests can be processed while waiting
       result = await model.generate_async(prompt)
       return result
   
   # Can handle 100+ requests/second per worker
   ```

💡 Key Async Concepts:

1. 🎯 Event Loop:
   ```python
   import asyncio
   
   async def main():
       tasks = [
           generate_text_async("สวัสดี"),
           generate_text_async("ราตรีสวัสดิ์"),
           generate_text_async("ลาก่อน")
       ]
       
       # Run concurrently, not sequentially!
       results = await asyncio.gather(*tasks)
       return results
   ```

2. 🔧 Async Context Managers:
   ```python
   class ModelManager:
       async def __aenter__(self):
           await self.load_model()
           return self
       
       async def __aexit__(self, exc_type, exc_val, exc_tb):
           await self.unload_model()
   
   # Usage
   async with ModelManager() as model:
       result = await model.generate("text")
   ```

3. 🌊 Streaming Responses:
   ```python
   from fastapi.responses import StreamingResponse
   
   async def stream_generator(prompt):
       async for token in model.stream_generate(prompt):
           yield f"data: {json.dumps({'token': token})}\\n\\n"
   
   @app.post("/stream")
   async def stream_text(prompt: str):
       return StreamingResponse(
           stream_generator(prompt),
           media_type="text/plain"
       )
   ```

⚠️ Common Async Pitfalls:
   • Mixing sync and async code incorrectly
   • Forgetting 'await' keyword
   • Using blocking operations in async functions
   • Not understanding the event loop
""")

def demonstrate_request_validation():
    """Demonstrate request validation with Pydantic."""
    print("""
🛡️ Request Validation with Pydantic:

🎯 Automatic Validation Benefits:
   • Type checking at runtime
   • Automatic error responses
   • Documentation generation
   • Data serialization/deserialization

📋 Validation Examples:

1. 🔤 Basic Field Validation:
   ```python
   from pydantic import BaseModel, Field, validator
   from typing import Literal, Optional
   
   class GenerateRequest(BaseModel):
       prompt: str = Field(..., min_length=1, max_length=2000)
       model: Literal["thai-model", "qwen-base"] = "thai-model"
       temperature: float = Field(0.7, ge=0.0, le=2.0)  # 0 <= temp <= 2
       max_tokens: int = Field(512, gt=0, le=2048)       # 0 < tokens <= 2048
       stream: bool = False
   
   # Invalid request automatically returns 422 error!
   ```

2. 🧮 Custom Validators:
   ```python
   class ChatRequest(BaseModel):
       messages: List[ChatMessage]
       temperature: Optional[float] = 0.7
       
       @validator('messages')
       def validate_messages(cls, v):
           if not v:
               raise ValueError('Messages cannot be empty')
           
           if v[-1].role != 'user':
               raise ValueError('Last message must be from user')
           
           return v
       
       @validator('temperature')
       def validate_temperature(cls, v):
           if v is not None and (v < 0 or v > 2):
               raise ValueError('Temperature must be between 0 and 2')
           return v
   ```

3. 📊 Response Models:
   ```python
   class GenerateResponse(BaseModel):
       text: str
       model: str
       created: int = Field(default_factory=lambda: int(time.time()))
       usage: Optional[dict] = None
       
       class Config:
           # Example response for documentation
           schema_extra = {
               "example": {
                   "text": "สวัสดีครับ! ยินดีที่ได้รู้จัก",
                   "model": "thai-model",
                   "created": 1698123456,
                   "usage": {"prompt_tokens": 10, "completion_tokens": 20}
               }
           }
   ```

✨ Validation Features:
   • Automatic HTTP 422 responses for invalid data
   • Detailed error messages with field-level info
   • Type coercion (string "123" → int 123)
   • Nested model validation
   • Custom error messages and codes
""")

def show_middleware_and_security():
    """Show middleware and security concepts."""
    print("""
🔐 Middleware & Security in FastAPI:

🛡️ Essential Middleware:

1. 🌍 CORS (Cross-Origin Resource Sharing):
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://myapp.com"],  # Specific origins
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

2. ⏱️ Rate Limiting:
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/generate")
   @limiter.limit("10/minute")  # 10 requests per minute per IP
   async def generate_limited(request: Request, prompt: str):
       return await generate_text(prompt)
   ```

3. 📝 Request Logging:
   ```python
   import time
   from fastapi import Request
   
   @app.middleware("http")
   async def log_requests(request: Request, call_next):
       start_time = time.time()
       
       # Log incoming request
       print(f"Request: {request.method} {request.url}")
       
       response = await call_next(request)
       
       # Log response time
       duration = time.time() - start_time
       print(f"Response: {response.status_code} in {duration:.3f}s")
       
       return response
   ```

🔑 Authentication & Authorization:

1. 🎫 API Key Authentication:
   ```python
   from fastapi import HTTPException, Depends
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   
   security = HTTPBearer()
   
   def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
       if credentials.credentials not in valid_api_keys:
           raise HTTPException(status_code=401, detail="Invalid API key")
       return credentials.credentials
   
   @app.post("/protected")
   async def protected_endpoint(
       data: dict,
       api_key: str = Depends(verify_api_key)
   ):
       return {"message": "Access granted"}
   ```

2. 🔐 JWT Token Authentication:
   ```python
   from jose import JWTError, jwt
   
   def verify_jwt_token(token: str = Depends(oauth2_scheme)):
       try:
           payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
           username = payload.get("sub")
           if username is None:
               raise credentials_exception
           return username
       except JWTError:
           raise credentials_exception
   ```

⚡ Performance Middleware:
   • Gzip compression for large responses
   • Response caching for repeated requests
   • Request/response size limits
   • Connection pooling for database/external APIs
""")

def main():
    print_header("Module 3.1: FastAPI Fundamentals")
    
    # Step 1: FastAPI Basics
    print_step(1, "FastAPI Fundamentals & Core Concepts")
    explain_fastapi_basics()
    
    input("\n🔍 Press Enter to analyze the actual API structure...")
    
    # Step 2: API Structure Analysis
    print_step(2, "Analyzing Thai Model API Structure")
    demonstrate_api_structure()
    
    input("\n🔍 Press Enter to learn about async programming...")
    
    # Step 3: Async Programming
    print_step(3, "Async/Await Programming")
    explain_async_programming()
    
    input("\n🔍 Press Enter to learn about request validation...")
    
    # Step 4: Request Validation
    print_step(4, "Request Validation with Pydantic")
    demonstrate_request_validation()
    
    input("\n🔍 Press Enter to learn about middleware and security...")
    
    # Step 5: Middleware & Security
    print_step(5, "Middleware & Security")
    show_middleware_and_security()
    
    input("\n🔍 Press Enter to see practical exercises...")
    
    # Step 6: Practical Exercises
    print_step(6, "Practical FastAPI Exercises")
    
    print("""
🧪 Hands-on FastAPI Experiments:

1. 🚀 Start the Thai Model API:
   ```bash
   cd /home/chanthaphan/project
   
   # Start the API server
   python scripts/api_server.py
   
   # Or use the detailed startup script
   python scripts/start_api.sh
   ```

2. 📖 Explore API Documentation:
   ```bash
   # Open in browser after starting server:
   # http://localhost:8000/docs        # Swagger UI
   # http://localhost:8000/redoc       # ReDoc
   
   # Or use curl to explore
   curl http://localhost:8000/
   curl http://localhost:8000/health
   ```

3. 🧪 Test API Endpoints:
   ```bash
   # Health check
   curl -X GET "http://localhost:8000/health"
   
   # Model info
   curl -X GET "http://localhost:8000/v1/models"
   
   # Chat completion
   curl -X POST "http://localhost:8000/v1/chat/completions" \\
     -H "Content-Type: application/json" \\
     -d '{
       "model": "thai-model",
       "messages": [{"role": "user", "content": "สวัสดีครับ"}],
       "temperature": 0.7,
       "max_tokens": 100
     }'
   ```

4. 📡 Test Streaming Response:
   ```bash
   curl -X POST "http://localhost:8000/v1/chat/completions" \\
     -H "Content-Type: application/json" \\
     -d '{
       "model": "thai-model", 
       "messages": [{"role": "user", "content": "เล่าเรื่องสั้นให้ฟัง"}],
       "stream": true
     }' \\
     --no-buffer
   ```

5. 🔍 Analyze API Code:
   ```python
   # Examine the actual API implementation
   with open('thai_model/api/fastapi_server.py', 'r') as f:
       content = f.read()
   
   # Look for key patterns
   import re
   endpoints = re.findall(r'@app\.(get|post|put|delete)\([^)]+\)', content)
   print("Endpoints found:", endpoints)
   
   # Find async functions
   async_funcs = re.findall(r'async def (\w+)', content)
   print("Async functions:", async_funcs)
   ```

6. 🛠️ Create Custom Endpoints:
   ```python
   # Add your own endpoint to the API
   @app.get("/custom/thai-greeting")
   async def thai_greeting(name: str = "friend"):
       greetings = ["สวัสดี", "ยินดีที่ได้รู้จัก", "ราตรีสวัสดิ์"]
       import random
       greeting = random.choice(greetings)
       return {"greeting": f"{greeting} {name}!"}
   ```

📊 Performance Testing:
   ```bash
   # Install tools for load testing
   pip install httpx asyncio
   
   # Simple async load test
   python -c "
   import asyncio
   import httpx
   import time
   
   async def test_endpoint():
       async with httpx.AsyncClient() as client:
           response = await client.get('http://localhost:8000/health')
           return response.status_code
   
   async def load_test(concurrent_requests=10):
       start = time.time()
       tasks = [test_endpoint() for _ in range(concurrent_requests)]
       results = await asyncio.gather(*tasks)
       duration = time.time() - start
       
       print(f'Completed {len(results)} requests in {duration:.2f}s')
       print(f'Rate: {len(results)/duration:.1f} requests/second')
   
   asyncio.run(load_test())
   "
   ```

🎯 Advanced Topics to Explore:

📚 API Design Patterns:
   • RESTful API principles
   • OpenAPI specification customization
   • API versioning strategies
   • Error handling best practices

⚡ Performance Optimization:
   • Connection pooling
   • Response caching
   • Batch request processing
   • Background task handling

🔐 Production Readiness:
   • Health checks and monitoring endpoints
   • Graceful shutdown handling
   • Configuration management
   • Logging and observability

🎯 Key Takeaways:
   • FastAPI provides automatic documentation and validation
   • Async/await enables high-performance APIs
   • Pydantic models ensure type safety and validation
   • Middleware adds cross-cutting concerns like security
   • The Thai Model API follows production best practices

🚀 Ready for Module 3.2: Advanced API Features!
""")

if __name__ == "__main__":
    main()
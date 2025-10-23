"""
FastAPI Server for Thai Model
============================

Production-ready API server with OpenAI-compatible endpoints for the Thai language model.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Generator
import json

from ..core import ThaiModel, ModelConfig
from .models import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThaiModelAPI:
    """
    Thai Model API server implementation.
    """
    
    def __init__(self, config: ModelConfig):
        """Initialize API with model configuration."""
        self.config = config
        self.model: Optional[ThaiModel] = None
        self.startup_time = time.time()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Thai Language Model API",
            version="1.0.0",
            description="Production-ready API for Thai language model with OpenAI-compatible endpoints",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
        
        # Register event handlers
        self._register_events()
    
    def _register_events(self):
        """Register startup and shutdown events."""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize resources on startup."""
            logger.info("🚀 Starting Thai Model API Server...")
            logger.info("📁 Model will be loaded on first request")
            logger.info(f"📋 Model: {self.config.model_name}")
        
        @self.app.on_event("shutdown") 
        async def shutdown_event():
            """Clean up resources on shutdown."""
            logger.info("🛑 Shutting down Thai Model API Server...")
            if self.model:
                self.model.unload_model()
    
    def _register_routes(self):
        """Register all API routes."""
        
        @self.app.get("/", response_model=APIInfoResponse)
        async def root():
            """Root endpoint with API information."""
            return APIInfoResponse(
                name="Thai Language Model API",
                version="1.0.0",
                description="Production-ready API for Thai language model",
                model=self.config.model_name,
                endpoints={
                    "chat": "/v1/chat/completions",
                    "summarize": "/v1/summarize", 
                    "generate": "/v1/generate",
                    "health": "/health",
                    "models": "/v1/models"
                },
                documentation="/docs"
            )
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            model_info = None
            if self.model and self.model.is_loaded:
                model_info = self.model.get_model_info()
            
            return HealthResponse(
                status="healthy",
                model_loaded=self.model.is_loaded if self.model else False,
                model_info=model_info,
                timestamp=int(time.time()),
                uptime=time.time() - self.startup_time
            )
        
        @self.app.get("/v1/models", response_model=ModelsResponse)
        async def list_models():
            """List available models (OpenAI-compatible)."""
            return ModelsResponse(
                object="list",
                data=[
                    ModelInfo(
                        id="thai-model",
                        created=int(self.startup_time),
                        owned_by="local",
                        root="thai-model"
                    )
                ]
            )
        
        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: ChatCompletionRequest):
            """OpenAI-compatible chat completions endpoint."""
            await self._ensure_model_loaded()
            
            try:
                # Convert messages to format expected by model
                messages = [{"role": msg.role.value, "content": msg.content} for msg in request.messages]
                
                # Generate response
                if request.stream:
                    return StreamingResponse(
                        self._stream_chat_completion(request, messages),
                        media_type="text/plain"
                    )
                else:
                    return await self._complete_chat_completion(request, messages)
                    
            except Exception as e:
                logger.error(f"Chat completion error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v1/summarize", response_model=SummarizeResponse)
        async def summarize_text(request: SummarizeRequest):
            """Custom endpoint for Thai text summarization."""
            await self._ensure_model_loaded()
            
            try:
                # Generate summary
                summary = self.model.summarize_text(
                    request.text,
                    max_length=request.max_tokens,
                    temperature=request.temperature
                )
                
                # Calculate metrics
                original_length = len(request.text.split())
                summary_length = len(summary.split())
                compression_ratio = summary_length / max(original_length, 1)
                
                # Estimate token usage (approximation)
                input_tokens = len(self.model.tokenizer.encode(request.text))
                output_tokens = len(self.model.tokenizer.encode(summary))
                
                return SummarizeResponse(
                    summary=summary,
                    original_length=original_length,
                    summary_length=summary_length,
                    compression_ratio=compression_ratio,
                    model="thai-model",
                    usage=Usage(
                        prompt_tokens=input_tokens,
                        completion_tokens=output_tokens,
                        total_tokens=input_tokens + output_tokens
                    )
                )
                
            except Exception as e:
                logger.error(f"Summarization error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v1/generate", response_model=GenerationResponse)
        async def generate_text(request: GenerationRequest):
            """General text generation endpoint."""
            await self._ensure_model_loaded()
            
            try:
                # Generate text
                if request.stream:
                    return StreamingResponse(
                        self._stream_generation(request),
                        media_type="text/plain"
                    )
                else:
                    generated_text = self.model.generate_text(
                        request.prompt,
                        max_new_tokens=request.max_tokens,
                        temperature=request.temperature,
                        top_p=request.top_p,
                        stream=False
                    )
                    
                    # Estimate token usage
                    input_tokens = len(self.model.tokenizer.encode(request.prompt))
                    output_tokens = len(self.model.tokenizer.encode(generated_text))
                    
                    return GenerationResponse(
                        generated_text=generated_text,
                        model="thai-model",
                        usage=Usage(
                            prompt_tokens=input_tokens,
                            completion_tokens=output_tokens,
                            total_tokens=input_tokens + output_tokens
                        )
                    )
                    
            except Exception as e:
                logger.error(f"Text generation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _ensure_model_loaded(self):
        """Ensure the model is loaded before processing requests."""
        if not self.model:
            logger.info("Loading Thai model...")
            self.model = ThaiModel(self.config)
        
        if not self.model.is_loaded:
            try:
                self.model.load_model()
                logger.info("✅ Thai model loaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")
    
    async def _complete_chat_completion(self, request: ChatCompletionRequest, messages: List[Dict]) -> ChatCompletionResponse:
        """Handle non-streaming chat completion."""
        response_text = self.model.chat_completion(
            messages,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            repetition_penalty=request.repetition_penalty,
            stream=False
        )
        
        # Estimate token usage
        prompt_text = " ".join([msg["content"] for msg in messages])
        input_tokens = len(self.model.tokenizer.encode(prompt_text))
        output_tokens = len(self.model.tokenizer.encode(response_text))
        
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=ChatMessage(role=MessageRole.ASSISTANT, content=response_text),
                    finish_reason=FinishReason.STOP
                )
            ],
            usage=Usage(
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens
            )
        )
    
    async def _stream_chat_completion(self, request: ChatCompletionRequest, messages: List[Dict]) -> Generator[str, None, None]:
        """Handle streaming chat completion."""
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created = int(time.time())
        
        # Start streaming
        for chunk in self.model.chat_completion(
            messages,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            repetition_penalty=request.repetition_penalty,
            stream=True
        ):
            chunk_data = ChatCompletionChunk(
                id=completion_id,
                created=created,
                model=request.model,
                choices=[{
                    "index": 0,
                    "delta": {"content": chunk},
                    "finish_reason": None
                }]
            )
            
            yield f"data: {chunk_data.json()}\n\n"
        
        # Send final chunk
        final_chunk = ChatCompletionChunk(
            id=completion_id,
            created=created,
            model=request.model,
            choices=[{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        )
        
        yield f"data: {final_chunk.json()}\n\n"
        yield "data: [DONE]\n\n"
    
    async def _stream_generation(self, request: GenerationRequest) -> Generator[str, None, None]:
        """Handle streaming text generation."""
        for chunk in self.model.generate_text(
            request.prompt,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stream=True
        ):
            yield chunk


def create_api_server(config: ModelConfig) -> FastAPI:
    """
    Factory function to create and configure the FastAPI server.
    
    Args:
        config: Model configuration
        
    Returns:
        Configured FastAPI application
    """
    api = ThaiModelAPI(config)
    return api.app


def main():
    """Run the FastAPI server."""
    from ..core.config import ModelConfig
    
    # Load configuration
    config = ModelConfig()
    
    # Create server
    app = create_api_server(config)
    
    print("🚀 Thai Model FastAPI Server")
    print("📋 Endpoints:")
    print("   - GET  /                     - API information")
    print("   - GET  /health               - Health check")
    print("   - GET  /v1/models            - List models")
    print("   - POST /v1/chat/completions  - Chat (OpenAI-compatible)")
    print("   - POST /v1/summarize         - Thai text summarization")
    print("   - POST /v1/generate          - General text generation")
    print()
    
    print("✅ Starting server...")
    print(f"🌐 Server URL: http://{config.api_host}:{config.api_port}")
    print(f"📚 API docs: http://{config.api_host}:{config.api_port}/docs")
    print("🔧 Use Ctrl+C to stop the server")
    print("-" * 60)
    
    # Run server
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        workers=config.api_workers,
        reload=False,
        access_log=True
    )


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
FastAPI server for hosting Thai model
Production-ready API server with OpenAI-compatible endpoints
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import uvicorn
import time
from pathlib import Path

# Request/Response models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict

class SummarizeRequest(BaseModel):
    text: str
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7

class SummarizeResponse(BaseModel):
    summary: str
    model: str
    usage: dict

class ThaiModelAPI:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self.base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
        self.lora_model_path = "./qwen_thai_lora"
    
    async def load_model(self):
        """Load the Thai model"""
        if self.model_loaded:
            return
        
        if not Path(self.lora_model_path).exists():
            raise HTTPException(status_code=500, detail="Thai model not found")
        
        try:
            print("Loading Thai model...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_name, 
                trust_remote_code=True
            )
            
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            
            # Load LoRA adapter
            self.model = PeftModel.from_pretrained(base_model, self.lora_model_path)
            self.model.eval()
            
            self.model_loaded = True
            print("✅ Thai model loaded successfully!")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading model: {e}")
    
    async def generate_text(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7):
        """Generate text using the Thai model"""
        await self.load_model()
        
        try:
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=450)
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3
                )
            
            # Decode
            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Calculate tokens used
            input_tokens = len(inputs['input_ids'][0])
            output_tokens = len(outputs[0]) - input_tokens
            
            return generated, input_tokens, output_tokens
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating text: {e}")

# Initialize FastAPI app and model
app = FastAPI(title="Thai Model API", version="1.0.0")
thai_model = ThaiModelAPI()

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    print("🚀 Starting Thai Model API Server...")
    print("📁 Model will be loaded on first request")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Thai Model API Server",
        "model": "Qwen2.5-1.5B-Instruct + Thai LoRA",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "summarize": "/v1/summarize",
            "health": "/health",
            "models": "/v1/models"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": thai_model.model_loaded,
        "timestamp": int(time.time())
    }

@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "thai-qwen-lora",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local",
                "permission": [],
                "root": "thai-qwen-lora",
                "parent": None
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    
    # Build prompt from messages
    prompt_parts = []
    for message in request.messages:
        if message.role == "user":
            # For Thai summarization, format as summarization task
            if "สรุป" in message.content or "summarize" in message.content.lower():
                prompt_parts.append(f"สรุปข่าวต่อไปนี้:\n\n{message.content}\n\nสรุป:")
            else:
                prompt_parts.append(f"User: {message.content}")
        elif message.role == "assistant":
            prompt_parts.append(f"Assistant: {message.content}")
        elif message.role == "system":
            prompt_parts.append(f"System: {message.content}")
    
    prompt = "\n".join(prompt_parts)
    
    # Generate response
    generated, input_tokens, output_tokens = await thai_model.generate_text(
        prompt, request.max_tokens, request.temperature
    )
    
    # Extract response (remove the prompt part)
    if "สรุป:" in generated:
        response_text = generated.split("สรุป:")[-1].strip()
    elif "Assistant:" in generated:
        response_text = generated.split("Assistant:")[-1].strip()
    else:
        response_text = generated.strip()
    
    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        model=request.model,
        choices=[
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ],
        usage={
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
    )

@app.post("/v1/summarize")
async def summarize_text(request: SummarizeRequest):
    """Custom endpoint for Thai text summarization"""
    
    # Create summarization prompt
    prompt = f"สรุปข่าวต่อไปนี้:\n\n{request.text}\n\nสรุป:"
    
    # Generate summary
    generated, input_tokens, output_tokens = await thai_model.generate_text(
        prompt, request.max_tokens, request.temperature
    )
    
    # Extract summary
    if "สรุป:" in generated:
        summary = generated.split("สรุป:")[-1].strip()
    else:
        summary = generated.strip()
    
    return SummarizeResponse(
        summary=summary,
        model="thai-qwen-lora",
        usage={
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
    )

def main():
    """Run the FastAPI server"""
    print("🚀 Thai Model FastAPI Server")
    print("📋 Endpoints:")
    print("   - GET  /                     - API information")
    print("   - GET  /health               - Health check")
    print("   - GET  /v1/models            - List models")
    print("   - POST /v1/chat/completions  - Chat (OpenAI-compatible)")
    print("   - POST /v1/summarize         - Thai text summarization")
    print()
    
    # Check if model exists
    model_path = Path("./qwen_thai_lora")
    if not model_path.exists():
        print("❌ Thai model not found at ./qwen_thai_lora")
        print("Please run 'python finetune_quen3_lora.py' first to train the model.")
        return 1
    
    print("✅ Thai model found")
    print("🌐 Starting server on http://localhost:8001")
    print("📚 API docs available at http://localhost:8001/docs")
    print("🔧 Use Ctrl+C to stop the server")
    print("-" * 60)
    
    # Run server
    uvicorn.run(
        "thai_model_api:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        access_log=True
    )

if __name__ == "__main__":
    main()
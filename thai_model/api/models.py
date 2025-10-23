"""
Pydantic Models for Thai Model API
=================================

Request and response models for the FastAPI server.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum

# Enums for better type safety
class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class FinishReason(str, Enum):
    STOP = "stop"
    LENGTH = "length"
    CONTENT_FILTER = "content_filter"

# Base models
class ChatMessage(BaseModel):
    """Individual chat message."""
    role: MessageRole
    content: str

class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Choice(BaseModel):
    """Chat completion choice."""
    index: int
    message: ChatMessage
    finish_reason: FinishReason

# Request models
class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = Field(default=150, ge=1, le=2048)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=50, ge=1, le=100)
    repetition_penalty: Optional[float] = Field(default=1.1, ge=1.0, le=2.0)
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None

class SummarizeRequest(BaseModel):
    """Thai text summarization request."""
    text: str = Field(..., min_length=10, max_length=10000)
    max_tokens: Optional[int] = Field(default=150, ge=10, le=500)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    language: Optional[str] = Field(default="thai", regex="^(thai|th|en|english)$")

class GenerationRequest(BaseModel):
    """General text generation request."""
    prompt: str = Field(..., min_length=1, max_length=5000)
    max_tokens: Optional[int] = Field(default=150, ge=1, le=1000)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    stream: Optional[bool] = False

# Response models
class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage

class SummarizeResponse(BaseModel):
    """Thai text summarization response."""
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    model: str
    usage: Usage

class GenerationResponse(BaseModel):
    """General text generation response."""
    generated_text: str
    model: str
    usage: Usage

class ModelInfo(BaseModel):
    """Model information."""
    id: str
    object: str = "model"
    created: int
    owned_by: str = "local"
    permission: List[str] = []
    root: Optional[str] = None
    parent: Optional[str] = None

class ModelsResponse(BaseModel):
    """List of available models."""
    object: str = "list"
    data: List[ModelInfo]

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    model_info: Optional[Dict[str, Any]] = None
    timestamp: int
    uptime: Optional[float] = None

class ErrorResponse(BaseModel):
    """Error response."""
    error: Dict[str, Any]

class APIInfoResponse(BaseModel):
    """API information response."""
    name: str
    version: str
    description: str
    model: str
    endpoints: Dict[str, str]
    documentation: str

# Streaming models
class ChatCompletionChunk(BaseModel):
    """Streaming chat completion chunk."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]

class StreamChoice(BaseModel):
    """Streaming choice delta."""
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[FinishReason] = None
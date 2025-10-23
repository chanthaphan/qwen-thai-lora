"""
API Module - FastAPI Server for Thai Model
==========================================

This module provides REST API endpoints for the Thai language model,
including OpenAI-compatible chat completions and custom endpoints.
"""

from .fastapi_server import create_api_server, ThaiModelAPI
from .models import *

__all__ = [
    "create_api_server",
    "ThaiModelAPI",
]
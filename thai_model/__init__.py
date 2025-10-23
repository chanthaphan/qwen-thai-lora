"""
Thai Language Model
==================

A comprehensive Thai language model package for fine-tuning, hosting, and inference.

This package provides:
- Fine-tuned Thai language models based on Qwen2.5
- REST API server with OpenAI-compatible endpoints
- Multiple user interfaces (CLI, Web GUI)
- Training and evaluation pipelines
- Docker deployment configurations

Author: Thai Model Team
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Thai Model Team"
__license__ = "MIT"

# Core imports - make them lazy to avoid import errors
# from .core import ThaiModel, ModelConfig
# from .api import create_api_server
# from .interfaces import ChatInterface, WebInterface

__all__ = [
    "ThaiModel",
    "ModelConfig", 
    "create_api_server",
    "ChatInterface",
    "WebInterface",
]
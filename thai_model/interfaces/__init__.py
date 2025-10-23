"""
Interfaces Module - User Interfaces for Thai Model
=================================================

This module provides various user interfaces for interacting with the Thai model,
including CLI, web GUI, and chat interfaces.
"""

from .cli import ChatInterface
from .web import WebInterface, create_web_interface

__all__ = [
    "ChatInterface",
    "WebInterface", 
    "create_web_interface",
]
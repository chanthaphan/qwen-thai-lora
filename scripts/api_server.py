#!/usr/bin/env python3
"""
Thai Model API Server Script
============================

Production-ready script to run the Thai Model API server.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from thai_model.core.config import ModelConfig
from thai_model.api.fastapi_server import main as run_server


def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(description="Thai Model API Server")
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/model_config.yaml",
        help="Path to model configuration file"
    )
    
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="Server host"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8001,
        help="Server port"
    )
    
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1,
        help="Number of worker processes"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if Path(args.config).exists():
        config = ModelConfig.from_yaml(args.config)
    else:
        print(f"⚠️  Configuration file not found: {args.config}")
        print("Using default configuration...")
        config = ModelConfig()
    
    # Override with command line arguments
    config.api_host = args.host
    config.api_port = args.port
    config.api_workers = args.workers
    
    # Run server
    run_server()


if __name__ == "__main__":
    main()
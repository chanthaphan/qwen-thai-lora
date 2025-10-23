"""
Thai Model Configuration
=======================

Configuration classes for the Thai language model.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import yaml
import json
from pathlib import Path

@dataclass
class ModelConfig:
    """Configuration for Thai model inference and serving."""
    
    # Model settings
    model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"
    model_path: Optional[str] = None
    adapter_path: Optional[str] = None
    device: str = "auto"
    torch_dtype: str = "float16"
    load_in_8bit: bool = False
    
    # Generation settings
    max_length: int = 2048
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_workers: int = 1
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "ModelConfig":
        """Load configuration from YAML file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
    
    @classmethod
    def from_json(cls, config_path: str) -> "ModelConfig":
        """Load configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls(**config_dict)
    
    def save_yaml(self, config_path: str):
        """Save configuration to YAML file."""
        config_dict = self.__dict__
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    def save_json(self, config_path: str):
        """Save configuration to JSON file."""
        config_dict = self.__dict__
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)


@dataclass  
class TrainingConfig:
    """Configuration for Thai model training."""
    
    # Model settings
    base_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    output_dir: str = "./models/checkpoints"
    
    # LoRA settings
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: List[str] = None
    
    # Training parameters
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 1
    per_device_eval_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    learning_rate: float = 2e-4
    warmup_steps: int = 100
    
    # Data settings
    dataset_name: str = "pythainlp/thaisum"
    max_seq_length: int = 1024
    train_split: str = "train"
    eval_split: str = "validation"
    
    # Optimization
    fp16: bool = True
    bf16: bool = False
    optim: str = "paged_adamw_32bit"
    weight_decay: float = 0.001
    
    # Logging and saving
    logging_steps: int = 50
    eval_steps: int = 200
    save_steps: int = 200
    save_total_limit: int = 3
    
    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "TrainingConfig":
        """Load training configuration from YAML file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)


@dataclass
class APIConfig:
    """Configuration for API server."""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8001
    workers: int = 1
    reload: bool = False
    
    # Model settings
    model_config_path: str = "config/model_config.yaml"
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_calls: int = 100
    rate_limit_period: int = 60
    
    # CORS settings
    cors_enabled: bool = True
    cors_origins: List[str] = None
    
    # Logging
    log_level: str = "INFO"
    access_log: bool = True
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]
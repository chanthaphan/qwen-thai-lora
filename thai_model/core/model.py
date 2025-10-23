"""
Thai Model Core Implementation
=============================

Main model class for Thai language model inference and management.
"""

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    GenerationConfig,
    TextIteratorStreamer
)
from peft import PeftModel, PeftConfig
from typing import Dict, List, Optional, Union, Iterator
import logging
from pathlib import Path
from threading import Thread

from .config import ModelConfig
from .tokenizer import ThaiTokenizer

logger = logging.getLogger(__name__)

class ThaiModel:
    """
    Main Thai Language Model class for inference and text generation.
    
    This class handles loading the base model and LoRA adapters,
    provides methods for text generation, and manages model configuration.
    """
    
    def __init__(self, config: ModelConfig):
        """
        Initialize Thai Model with configuration.
        
        Args:
            config: ModelConfig instance with model settings
        """
        self.config = config
        self.model = None
        self.tokenizer = None
        self.thai_tokenizer = None
        self.device = self._setup_device()
        self.is_loaded = False
        
    def _setup_device(self) -> torch.device:
        """Setup and return the appropriate device for model inference."""
        if self.config.device == "auto":
            if torch.cuda.is_available():
                device = torch.device("cuda")
                logger.info(f"Using CUDA device: {torch.cuda.get_device_name()}")
            else:
                device = torch.device("cpu")
                logger.info("Using CPU device")
        else:
            device = torch.device(self.config.device)
            logger.info(f"Using specified device: {device}")
        
        return device
    
    def load_model(self) -> None:
        """Load the base model and LoRA adapters if specified."""
        try:
            logger.info(f"Loading model: {self.config.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path or self.config.model_name,
                trust_remote_code=True
            )
            
            # Ensure pad token exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Initialize Thai tokenizer
            self.thai_tokenizer = ThaiTokenizer(self.tokenizer)
            
            # Load base model
            model_kwargs = {
                "trust_remote_code": True,
                "device_map": "auto" if self.config.device == "auto" else None,
            }
            
            if self.config.torch_dtype == "float16":
                model_kwargs["torch_dtype"] = torch.float16
            elif self.config.torch_dtype == "bfloat16":
                model_kwargs["torch_dtype"] = torch.bfloat16
                
            if self.config.load_in_8bit:
                model_kwargs["load_in_8bit"] = True
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path or self.config.model_name,
                **model_kwargs
            )
            
            # Load LoRA adapter if specified
            if self.config.adapter_path and Path(self.config.adapter_path).exists():
                logger.info(f"Loading LoRA adapter: {self.config.adapter_path}")
                self.model = PeftModel.from_pretrained(
                    self.model, 
                    self.config.adapter_path
                )
            
            # Move to device if not using device_map
            if self.config.device != "auto":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            self.is_loaded = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate_text(
        self, 
        prompt: str, 
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """
        Generate text based on input prompt.
        
        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            repetition_penalty: Repetition penalty
            stream: Whether to return streaming response
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text or iterator of text chunks if streaming
        """
        if not self.is_loaded:
            self.load_model()
        
        # Use config defaults if parameters not specified
        generation_config = GenerationConfig(
            max_new_tokens=max_new_tokens or self.config.max_new_tokens,
            temperature=temperature or self.config.temperature,
            top_p=top_p or self.config.top_p,
            top_k=top_k or self.config.top_k,
            repetition_penalty=repetition_penalty or self.config.repetition_penalty,
            pad_token_id=self.tokenizer.eos_token_id,
            do_sample=True,
            **kwargs
        )
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True,
            max_length=self.config.max_length - generation_config.max_new_tokens
        )
        
        if self.device.type == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        if stream:
            return self._generate_stream(inputs, generation_config)
        else:
            return self._generate_complete(inputs, generation_config)
    
    def _generate_complete(self, inputs: Dict, generation_config: GenerationConfig) -> str:
        """Generate complete response."""
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                generation_config=generation_config,
                use_cache=True
            )
        
        # Decode response
        generated_text = self.tokenizer.decode(
            outputs[0][len(inputs["input_ids"][0]):], 
            skip_special_tokens=True
        )
        
        return generated_text.strip()
    
    def _generate_stream(self, inputs: Dict, generation_config: GenerationConfig) -> Iterator[str]:
        """Generate streaming response."""
        streamer = TextIteratorStreamer(
            self.tokenizer, 
            timeout=60.0, 
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        generation_kwargs = {
            **inputs,
            "generation_config": generation_config,
            "streamer": streamer,
            "use_cache": True
        }
        
        # Start generation in separate thread
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # Yield tokens as they are generated
        for new_text in streamer:
            yield new_text
        
        thread.join()
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """
        Generate chat completion response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response or iterator if streaming
        """
        # Convert messages to prompt format
        prompt = self.thai_tokenizer.format_chat_prompt(messages)
        
        return self.generate_text(prompt, **kwargs)
    
    def summarize_text(
        self, 
        text: str, 
        max_length: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate Thai text summarization.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            **kwargs: Additional generation parameters
            
        Returns:
            Generated summary
        """
        prompt = f"สรุปข้อความต่อไปนี้:\n\n{text}\n\nสรุป:"
        
        max_new_tokens = min(max_length or 200, len(text.split()) // 2)
        
        return self.generate_text(
            prompt, 
            max_new_tokens=max_new_tokens,
            stream=False,
            **kwargs
        )
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the loaded model."""
        if not self.is_loaded:
            return {"status": "not_loaded"}
        
        info = {
            "status": "loaded",
            "model_name": self.config.model_name,
            "model_path": self.config.model_path,
            "adapter_path": self.config.adapter_path,
            "device": str(self.device),
            "torch_dtype": self.config.torch_dtype,
            "vocab_size": self.tokenizer.vocab_size if self.tokenizer else None,
        }
        
        # Add memory usage if on GPU
        if self.device.type == "cuda":
            info["gpu_memory"] = {
                "allocated": torch.cuda.memory_allocated(self.device),
                "cached": torch.cuda.memory_reserved(self.device)
            }
        
        return info
    
    def unload_model(self) -> None:
        """Unload the model to free memory."""
        if self.model:
            del self.model
            self.model = None
        
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
            
        if self.thai_tokenizer:
            del self.thai_tokenizer
            self.thai_tokenizer = None
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_loaded = False
        logger.info("Model unloaded successfully")
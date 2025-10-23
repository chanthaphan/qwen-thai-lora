#!/usr/bin/env python3
"""
Module 1.2: Configuration Management
==================================

Interactive learning script to master YAML-based configuration and dataclasses.
"""

import os
import sys
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎓 {title}")
    print(f"{'='*60}\n")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"📚 Step {step_num}: {description}")
    print("-" * 40)

def main():
    print_header("Module 1.2: Configuration Management")
    
    project_root = Path(__file__).parent.parent
    config_dir = project_root / "config"
    
    # Step 1: Understanding YAML Configuration
    print_step(1, "Understanding YAML Configuration Files")
    
    if config_dir.exists():
        print(f"📁 Configuration directory: {config_dir}")
        
        for config_file in config_dir.glob("*.yaml"):
            print(f"\n📄 {config_file.name}:")
            try:
                with open(config_file, 'r') as f:
                    content = yaml.safe_load(f)
                
                # Pretty print the YAML structure
                import json
                print(json.dumps(content, indent=2))
                
            except Exception as e:
                print(f"❌ Error reading {config_file}: {e}")
    
    input("\n🔍 Press Enter to continue to Step 2...")
    
    # Step 2: Dataclasses vs Regular Classes
    print_step(2, "Dataclasses vs Regular Classes")
    
    print("🏗️ Regular Class Example:")
    print("""
class RegularConfig:
    def __init__(self, model_name, max_length=512, temperature=0.7):
        self.model_name = model_name
        self.max_length = max_length
        self.temperature = temperature
    
    def __repr__(self):
        return f"RegularConfig(model_name='{self.model_name}', ...)"
""")
    
    print("\n🚀 Dataclass Example:")
    print("""
@dataclass
class DataclassConfig:
    model_name: str
    max_length: int = 512
    temperature: float = 0.7
    
    # Automatic __init__, __repr__, __eq__ methods!
""")
    
    # Demonstrate the difference
    @dataclass
    class ExampleConfig:
        model_name: str
        max_length: int = 512
        temperature: float = 0.7
        metadata: Dict[str, Any] = field(default_factory=dict)
    
    config1 = ExampleConfig("test-model")
    config2 = ExampleConfig("test-model")
    
    print(f"\n📊 Dataclass instance: {config1}")
    print(f"🔄 Equality check: config1 == config2 -> {config1 == config2}")
    print(f"🏷️ Type annotations help IDEs and type checkers!")
    
    input("\n🔍 Press Enter to continue to Step 3...")
    
    # Step 3: Loading Configuration from YAML
    print_step(3, "Loading Configuration from YAML")
    
    # Try to import the actual config class
    try:
        sys.path.insert(0, str(project_root))
        from thai_model.core.config import ModelConfig
        
        print("🧪 Testing ModelConfig.from_yaml():")
        
        model_config_path = config_dir / "model_config.yaml"
        if model_config_path.exists():
            try:
                config = ModelConfig.from_yaml(str(model_config_path))
                print(f"✅ Loaded config: {config}")
                
                print(f"\n📊 Configuration attributes:")
                for attr, value in config.__dict__.items():
                    print(f"  • {attr}: {value}")
                
            except Exception as e:
                print(f"❌ Error loading config: {e}")
        else:
            print(f"❌ Config file not found: {model_config_path}")
            
    except ImportError as e:
        print(f"❌ Could not import ModelConfig: {e}")
        print("💡 This might be due to missing dependencies")
    
    input("\n🔍 Press Enter to continue to Step 4...")
    
    # Step 4: Creating Custom Configuration
    print_step(4, "Creating Custom Configuration")
    
    # Create a simple custom config example
    @dataclass
    class CustomAPIConfig:
        host: str = "localhost"
        port: int = 8000
        workers: int = 1
        log_level: str = "info"
        enable_cors: bool = True
        api_keys: Dict[str, str] = field(default_factory=dict)
        
        def to_yaml(self, filepath: str):
            """Save configuration to YAML file."""
            config_dict = {
                'server': {
                    'host': self.host,
                    'port': self.port,
                    'workers': self.workers,
                    'log_level': self.log_level
                },
                'features': {
                    'enable_cors': self.enable_cors
                },
                'security': {
                    'api_keys': self.api_keys
                }
            }
            
            with open(filepath, 'w') as f:
                yaml.dump(config_dict, f, indent=2)
            print(f"✅ Configuration saved to: {filepath}")
        
        @classmethod
        def from_yaml(cls, filepath: str):
            """Load configuration from YAML file."""
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            return cls(
                host=data['server']['host'],
                port=data['server']['port'],
                workers=data['server']['workers'],
                log_level=data['server']['log_level'],
                enable_cors=data['features']['enable_cors'],
                api_keys=data['security']['api_keys']
            )
    
    # Demonstrate custom config
    print("🏗️ Creating custom configuration:")
    custom_config = CustomAPIConfig(
        host="0.0.0.0",
        port=8080,
        api_keys={"admin": "secret123"}
    )
    
    print(f"📊 Custom config: {custom_config}")
    
    # Save and load example
    temp_config_path = "/tmp/custom_api_config.yaml"
    custom_config.to_yaml(temp_config_path)
    
    print(f"\n📄 Saved YAML content:")
    with open(temp_config_path, 'r') as f:
        print(f.read())
    
    # Load it back
    loaded_config = CustomAPIConfig.from_yaml(temp_config_path)
    print(f"\n🔄 Loaded config: {loaded_config}")
    print(f"✅ Configs match: {custom_config == loaded_config}")
    
    # Cleanup
    os.remove(temp_config_path)
    
    input("\n🔍 Press Enter to continue to Step 5...")
    
    # Step 5: Environment Variables and Config Hierarchy
    print_step(5, "Environment Variables & Config Hierarchy")
    
    print("🌍 Configuration hierarchy (highest to lowest priority):")
    print("1. Command line arguments")
    print("2. Environment variables")
    print("3. Configuration files")
    print("4. Default values")
    
    # Demonstrate environment variable override
    @dataclass
    class EnvAwareConfig:
        model_name: str = "default-model"
        api_key: Optional[str] = None
        debug: bool = False
        
        def __post_init__(self):
            """Override with environment variables if available."""
            self.model_name = os.getenv('MODEL_NAME', self.model_name)
            self.api_key = os.getenv('API_KEY', self.api_key)
            self.debug = os.getenv('DEBUG', str(self.debug)).lower() == 'true'
    
    print(f"\n🧪 Testing environment variable override:")
    
    # Set a test environment variable
    os.environ['MODEL_NAME'] = 'env-override-model'
    os.environ['DEBUG'] = 'true'
    
    env_config = EnvAwareConfig()
    print(f"📊 Config with env vars: {env_config}")
    
    # Clean up
    del os.environ['MODEL_NAME']
    del os.environ['DEBUG']
    
    input("\n🔍 Press Enter to see summary...")
    
    # Summary
    print_step("Summary", "What You Learned")
    
    print("""
🎯 Key Concepts Covered:
  • YAML configuration files and structure
  • Dataclasses for type-safe configuration
  • Loading and saving configuration to/from YAML
  • Environment variable overrides
  • Configuration hierarchy and best practices

📚 Configuration Best Practices:
  1. Use dataclasses for type safety
  2. Provide sensible defaults
  3. Support environment variable overrides
  4. Validate configuration values
  5. Use hierarchical configuration files

💡 Pro Tips:
  • Use typing hints for better IDE support
  • Implement validation in __post_init__
  • Consider using Pydantic for complex validation
  • Keep secrets in environment variables, not config files
  • Use different config files for different environments

🔍 Hands-on Exercises:
  1. Modify config/model_config.yaml and reload
  2. Create your own dataclass with validation
  3. Implement environment variable overrides
  4. Try using Pydantic BaseSettings for advanced config
    
🚀 Ready for Module 2.1: Understanding Transformers & LoRA!
""")

if __name__ == "__main__":
    main()
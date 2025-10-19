#!/usr/bin/env python3
"""
Merge LoRA adapter with base model for vLLM hosting
This script merges your Thai LoRA adapter with the base Qwen model
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import sys
from pathlib import Path

def merge_lora_model():
    """Merge LoRA adapter with base model and save the merged model"""
    
    base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    lora_model_path = "./models/qwen_thai_lora"
    merged_model_path = "./models/qwen_thai_merged"
    
    # Check if LoRA model exists
    if not Path(lora_model_path).exists():
        print("❌ Thai LoRA model not found at ./qwen_thai_lora")
        print("Please run finetune_quen3_lora.py first to create the model")
        return 1
    
    # Check if merged model already exists
    if Path(merged_model_path).exists():
        response = input(f"⚠️  Merged model already exists at {merged_model_path}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled by user")
            return 1
        
        # Remove existing directory
        import shutil
        shutil.rmtree(merged_model_path)
    
    print("🔄 Merging LoRA adapter with base model...")
    print(f"📁 Base model: {base_model_name}")
    print(f"📁 LoRA adapter: {lora_model_path}")
    print(f"📁 Output: {merged_model_path}")
    
    try:
        # Load tokenizer
        print("📝 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
        
        # Load base model
        print("🤖 Loading base model...")
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Load LoRA adapter
        print("🔧 Loading LoRA adapter...")
        model = PeftModel.from_pretrained(base_model, lora_model_path)
        
        # Merge LoRA weights into base model
        print("⚡ Merging LoRA weights...")
        merged_model = model.merge_and_unload()
        
        # Save merged model
        print("💾 Saving merged model...")
        merged_model.save_pretrained(merged_model_path)
        tokenizer.save_pretrained(merged_model_path)
        
        print("✅ Model merged successfully!")
        print(f"📁 Merged model saved to: {merged_model_path}")
        print("\n🚀 Now you can use vLLM with the merged model:")
        print(f"   ./llm-env/bin/python -m vllm.entrypoints.openai.api_server \\")
        print(f"     --model {merged_model_path} \\")
        print(f"     --host 0.0.0.0 --port 8000 \\")
        print(f"     --served-model-name thai-qwen-merged")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error merging model: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Main function"""
    print("🔄 Thai LoRA Model Merger")
    print("This script merges your LoRA adapter with the base model for vLLM hosting")
    print("-" * 60)
    
    # Check if we have GPU
    if torch.cuda.is_available():
        print(f"🎮 GPU detected: {torch.cuda.get_device_name()}")
    else:
        print("⚠️  No GPU detected. Merging will be slower on CPU.")
    
    # Estimate memory requirement
    print("💾 Memory requirement: ~3-4GB GPU memory or 8GB RAM")
    
    confirm = input("\n🚀 Proceed with model merging? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled by user")
        return 1
    
    return merge_lora_model()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
Simple test script for Thai model
This script directly tests the model without needing a server
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append('/home/chanthaphan/project')

def test_thai_model():
    """Test the Thai model directly"""
    try:
        print("🧪 Testing Thai Model Directly...")
        print("-" * 40)
        
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel
        
        base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
        lora_model_path = "./models/qwen_thai_lora"
        
        print("📁 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
        
        print("🤖 Loading base model...")
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        print("🔧 Loading LoRA adapter...")
        model = PeftModel.from_pretrained(base_model, lora_model_path)
        model.eval()
        
        print("✅ Model loaded successfully!")
        
        # Test Thai text
        test_text = "นักวิทยาศาสตร์ได้พัฒนาเทคโนโลยีปัญญาประดิษฐ์ใหม่ที่สามารถช่วยในการวินิจฉัยโรคมะเร็งได้อย่างแม่นยำมากขึ้น"
        prompt = f"สรุปข่าวต่อไปนี้:\n\n{test_text}\n\nสรุป:"
        
        print(f"📝 Input: {test_text}")
        print("🔄 Generating summary...")
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=450)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=3
            )
        
        # Decode
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract summary
        if "สรุป:" in generated:
            summary = generated.split("สรุป:")[-1].strip()
        else:
            summary = generated.strip()
        
        print(f"✨ Summary: {summary}")
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_thai_model()
    if success:
        print("\n🚀 Your Thai model is working perfectly!")
        print("💡 You can now use it with:")
        print("   - ./llm-env/bin/python thai_model_gui.py")
        print("   - ./llm-env/bin/python host_thai_model.py")
    else:
        print("\n❌ Model test failed. Check the error messages above.")
    
    sys.exit(0 if success else 1)
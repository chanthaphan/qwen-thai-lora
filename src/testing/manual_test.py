#!/usr/bin/env python3
"""
Interactive Test Script
Quick manual testing of the Thai model
"""

import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

def load_model():
    """Load the Thai model"""
    print("🔧 Loading Thai model...")
    
    base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    lora_path = "./models/qwen_thai_lora"
    
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    model = PeftModel.from_pretrained(base_model, lora_path)
    model.eval()
    
    print("✅ Model loaded successfully!")
    return model, tokenizer

def test_summarization(model, tokenizer, text):
    """Test summarization on given text"""
    prompt = f"สรุปข่าวต่อไปนี้:\n\n{text}\n\nสรุป:"
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=450)
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    
    print("🔄 Generating summary...")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=120,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=3
        )
    
    generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract summary
    if "สรุป:" in generated:
        summary = generated.split("สรุป:")[-1].strip()
    else:
        summary = generated.strip()
    
    return summary

def interactive_test():
    """Interactive testing mode"""
    model, tokenizer = load_model()
    
    print("\n🧪 Interactive Thai Model Testing")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for sample texts")
    
    sample_texts = [
        "นักวิทยาศาสตร์ได้พัฒนาเทคโนโลยีใหม่ที่สามารถตรวจจับโรคมะเร็งได้แม่นยำขึ้น โดยใช้ปัญญาประดิษฐ์ในการวิเคราะห์ภาพถ่ายทางการแพทย์",
        "รัฐบาลประกาศนโยบายส่งเสริมพลังงานสะอาด เพื่อลดการปล่อยก๊าซเรือนกระจกและสนับสนุนเทคโนโลยีที่เป็นมิตรกับสิ่งแวดล้อม",
        "การศึกษาใหม่พบว่าการออกกำลังกายสม่ำเสมอช่วยเพิ่มความสุขและลดความเครียด รวมทั้งปรับปรุงคุณภาพการนอนหลับ"
    ]
    
    while True:
        print(f"\n📝 Enter Thai text to summarize:")
        user_input = input("> ").strip()
        
        if user_input.lower() == 'quit':
            print("👋 Goodbye!")
            break
        elif user_input.lower() == 'help':
            print("\n📋 Sample texts you can try:")
            for i, sample in enumerate(sample_texts, 1):
                print(f"{i}. {sample}")
            continue
        elif user_input.isdigit() and 1 <= int(user_input) <= len(sample_texts):
            user_input = sample_texts[int(user_input) - 1]
            print(f"📄 Using sample text: {user_input}")
        elif not user_input:
            print("⚠️  Please enter some text")
            continue
        
        try:
            summary = test_summarization(model, tokenizer, user_input)
            print(f"\n✨ Summary: {summary}")
            print(f"📊 Original: {len(user_input)} chars → Summary: {len(summary)} chars")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        model, tokenizer = load_model()
        text = " ".join(sys.argv[1:])
        print(f"\n📄 Input text: {text}")
        
        try:
            summary = test_summarization(model, tokenizer, text)
            print(f"\n✨ Summary: {summary}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        # Interactive mode
        interactive_test()

if __name__ == "__main__":
    main()
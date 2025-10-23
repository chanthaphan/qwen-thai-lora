#!/usr/bin/env python3
"""
Test script สำหรับทดสอบโมเดลที่ Fine-tune แล้ว
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

def test_thai_summarization():
    # โหลดโมเดลและ tokenizer
    base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    lora_model_path = "./models/qwen_thai_lora"
    
    print("Loading base model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(base_model, lora_model_path)
    model.eval()
    
    # ข้อมูลทดสอบ
    test_articles = [
        """นักวิทยาศาสตร์จากมหาวิทยาลัยชั้นนำได้พัฒนาเทคโนโลジีปัญญาประดิษฐ์ใหม่ที่สามารถช่วยในการวินิจฉัยโรคมะเร็งได้อย่างแม่นยำมากขึ้น โดยใช้การเรียนรู้เชิงลึกในการวิเคราะห์ภาพถ่ายทางการแพทย์ จากการทดสอบพบว่าระบบนี้สามารถตระหนักถึงความผิดปกติได้ถึง 95% ซึ่งสูงกว่าการวินิจฉัยแบบดั้งเดิมถึง 15% นอกจากนี้ระบบยังสามารถให้ผลการวินิจฉัยได้เร็วกว่าเดิมถึง 3 เท่า""",
        
        """รัฐบาลได้ประกาศนโยบายใหม่เพื่อส่งเสริมการใช้พลังงานสะอาดและพลังงานทดแทน โดยเฉพาะพลังงานแสงอาทิตย์และพลังงานลม เป้าหมายคือการลดการปล่อยก๊าซเรือนกระจกลง 30% ภายในปี 2030 พร้อมทั้งสนับสนุนการลงทุนในเทคโนโลยีสะอาด รัฐบาลจะให้สิทธิประโยชน์ทางภาษีแก่ผู้ประกอบการที่ลงทุนในโครงการพลังงานสะอาด""",
        
        """การศึกษาวิจัยใหม่พบว่าการออกกำลังกายสม่ำเสมออย่างน้อย 30 นาทีต่อวัน ไม่เพียงแต่ช่วยให้ร่างกายแข็งแรงและลดน้ำหนัก แต่ยังมีประโยชน์ต่อสุขภาพจิตอย่างมาก สามารถลดความเครียด ความวิตกกังวล และช่วยปรับปรุงคุณภาพการนอนหลับ นักวิจัยแนะนำให้เลือกกิจกรรมที่ชอบ เช่น เดิน วิ่ง ว่ายน้ำ หรือโยคะ"""
    ]
    
    print("\n" + "="*60)
    print("ทดสอบการสรุปข่าวภาษาไทย")
    print("="*60)
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n📰 ข่าวที่ {i}:")
        print("-" * 40)
        print(f"📄 ข่าวต้นฉบับ:\n{article}")
        print("\n" + "." * 40)
        
        # สร้าง prompt
        prompt = f"สรุปข่าวต่อไปนี้:\n\n{article}\n\nสรุป:"
        
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
        
        # แยกเฉพาะส่วนสรุปที่สร้างขึ้น
        try:
            summary = generated.split("สรุป:")[-1].strip()
        except:
            summary = generated
            
        print(f"🔍 สรุป: {summary}")
        print()

if __name__ == "__main__":
    test_thai_summarization()
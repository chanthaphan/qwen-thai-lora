#!/usr/bin/env python3
"""
Model Evaluation Script
This script evaluates the Thai model performance on various tasks
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
import time
from datetime import datetime

class ThaiModelEvaluator:
    def __init__(self, base_model_name="Qwen/Qwen2.5-1.5B-Instruct", lora_path="./models/qwen_thai_lora"):
        """Initialize the evaluator"""
        print("🔧 Initializing Thai Model Evaluator...")
        
        self.base_model_name = base_model_name
        self.lora_path = lora_path
        
        # Load model
        print("📁 Loading tokenizer and model...")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
        
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        self.model = PeftModel.from_pretrained(base_model, lora_path)
        self.model.eval()
        
        print("✅ Model loaded successfully!")
    
    def generate_summary(self, text, max_tokens=100):
        """Generate a summary for given text"""
        prompt = f"สรุปข่าวต่อไปนี้:\n\n{text}\n\nสรุป:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=450)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        start_time = time.time()
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3
            )
        
        generation_time = time.time() - start_time
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract summary
        if "สรุป:" in generated:
            summary = generated.split("สรุป:")[-1].strip()
        else:
            summary = generated.strip()
        
        return summary, generation_time
    
    def evaluate_test_cases(self):
        """Run evaluation on predefined test cases"""
        test_cases = [
            {
                "id": 1,
                "category": "Technology",
                "text": "บริษัทเทคโนโลยีชั้นนำได้พัฒนาระบบปัญญาประดิษฐ์ใหม่ที่สามารถแปลภาษาไทยได้อย่างแม่นยำ โดยใช้เทคโนโลยี Deep Learning ขั้นสูง ระบบนี้สามารถแปลข้อความที่ซับซ้อนและมีบริบททางวัฒนธรรมได้ดี ผลการทดสอบพบว่าความแม่นยำสูงถึง 98% ซึ่งเป็นความก้าวหน้าที่สำคัญในด้านการประมวลผลภาษาไทย",
                "expected_topics": ["เทคโนโลยี", "ปัญญาประดิษฐ์", "การแปลภาษา"]
            },
            {
                "id": 2,
                "category": "Health",
                "text": "การศึกษาวิจัยใหม่จากคณะแพทยศาสตร์พบว่าการรับประทานผลไม้และผักสีเข้มสม่ำเสมอสามารถช่วยลดความเสี่ยงของโรคหัวใจได้ถึง 40% โดยสารต้านอนุมูลอิสระในผักและผลไม้เหล่านี้ช่วยปกป้องหลอดเลือดและลดการอักเสบ นักวิจัยแนะนำให้รับประทานผลไม้ผักสีเข้มอย่างน้อย 5 ส่วนต่อวัน",
                "expected_topics": ["สุขภาพ", "โรคหัวใจ", "ผลไม้ผัก"]
            },
            {
                "id": 3,
                "category": "Environment",
                "text": "โครงการปลูกป่าชายเลนขนาดใหญ่ได้เริ่มขึ้นในภาคใต้ เพื่อฟื้นฟูระบบนิเวศทางทะเลและลดผลกระทบจากการเปลี่ยนแปลงสภาพภูมิอากาศ โครงการนี้คาดว่าจะปลูกต้นไม้กว่า 100,000 ต้น ครอบคลุมพื้นที่ 500 ไร่ และจะช่วยดูดซับคาร์บอนไดออกไซด์ได้ปีละ 5,000 ตัน พร้อมทั้งเป็นแหล่งที่อยู่ของสัตว์น้ำและนกหายาก",
                "expected_topics": ["สิ่งแวดล้อม", "ป่าชายเลน", "สภาพภูมิอากาศ"]
            }
        ]
        
        results = []
        total_time = 0
        
        print("\n🧪 Running Model Evaluation...")
        print("=" * 60)
        
        for case in test_cases:
            print(f"\n📋 Test Case {case['id']} - {case['category']}")
            print("-" * 40)
            print(f"📄 Original: {case['text'][:100]}...")
            
            summary, gen_time = self.generate_summary(case['text'])
            total_time += gen_time
            
            print(f"✨ Summary: {summary}")
            print(f"⏱️  Generation time: {gen_time:.2f}s")
            
            # Simple evaluation metrics
            original_length = len(case['text'])
            summary_length = len(summary)
            compression_ratio = summary_length / original_length
            
            result = {
                "test_id": case['id'],
                "category": case['category'],
                "original_text": case['text'],
                "generated_summary": summary,
                "original_length": original_length,
                "summary_length": summary_length,
                "compression_ratio": compression_ratio,
                "generation_time": gen_time,
                "expected_topics": case['expected_topics']
            }
            
            results.append(result)
            
            print(f"📊 Length: {original_length} → {summary_length} chars (compression: {compression_ratio:.2f})")
        
        # Summary statistics
        avg_time = total_time / len(test_cases)
        avg_compression = sum(r['compression_ratio'] for r in results) / len(results)
        
        print(f"\n📈 Evaluation Summary:")
        print(f"   • Total test cases: {len(test_cases)}")
        print(f"   • Average generation time: {avg_time:.2f}s")
        print(f"   • Average compression ratio: {avg_compression:.2f}")
        print(f"   • Total evaluation time: {total_time:.2f}s")
        
        return results
    
    def save_evaluation_report(self, results, filename=None):
        """Save evaluation results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_report_{timestamp}.json"
        
        report = {
            "evaluation_date": datetime.now().isoformat(),
            "model_info": {
                "base_model": self.base_model_name,
                "lora_path": self.lora_path
            },
            "test_results": results,
            "summary_stats": {
                "total_cases": len(results),
                "avg_generation_time": sum(r['generation_time'] for r in results) / len(results),
                "avg_compression_ratio": sum(r['compression_ratio'] for r in results) / len(results)
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Evaluation report saved: {filename}")
        return filename

def main():
    """Main evaluation function"""
    try:
        evaluator = ThaiModelEvaluator()
        results = evaluator.evaluate_test_cases()
        report_file = evaluator.save_evaluation_report(results)
        
        print(f"\n🎉 Evaluation completed successfully!")
        print(f"📋 Report saved: {report_file}")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
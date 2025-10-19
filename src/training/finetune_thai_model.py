from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer
import torch, os
import numpy as np
from rouge_score import rouge_scorer
from sklearn.metrics import accuracy_score
import json

# ใช้โมเดล Qwen2.5 ที่มีอยู่จริง หรือ fallback เป็นโมเดลที่เข้าถึงได้
model_name = "Qwen/Qwen2.5-1.5B-Instruct"   # ใช้โมเดลเล็กกว่าที่เข้าถึงได้
dataset_name = "pythainlp/thaisum"         # Thai summarization dataset (real one)

print(f"Loading model: {model_name}")

# โหลด tokenizer / model พร้อม error handling
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    print("Tokenizer loaded successfully")
except Exception as e:
    print(f"Error loading tokenizer: {e}")
    # Fallback เป็นโมเดลที่เข้าถึงได้แน่นอน
    model_name = "microsoft/DialoGPT-medium"
    print(f"Fallback to model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    # เพิ่ม pad_token ถ้าไม่มี
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
try:
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        load_in_8bit=True,            # ใช้ 8-bit เพื่อประหยัด VRAM
        trust_remote_code=True,
    )
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model with 8-bit: {e}")
    # ลองโหลดแบบปกติ
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            trust_remote_code=True,
        )
        print("Model loaded successfully (without 8-bit)")
    except Exception as e2:
        print(f"Error loading model: {e2}")
        raise e2

# ตั้งค่า LoRA adapter
try:
    # สำหรับ Qwen models
    target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]
    if "DialoGPT" in model_name:
        # สำหรับ DialoGPT
        target_modules = ["c_attn", "c_proj"]
    
    peft_config = LoraConfig(
        r=16, 
        lora_alpha=32,
        target_modules=target_modules,  # ปรับตาม model architecture
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)
    print("LoRA adapter configured successfully")
except Exception as e:
    print(f"Error configuring LoRA: {e}")
    # ใช้ target_modules ทั่วไป
    peft_config = LoraConfig(
        r=8, 
        lora_alpha=16,
        target_modules=["attn", "mlp"],  # ชื่อทั่วไป
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)
    print("LoRA adapter configured with generic targets")

# โหลดชุดข้อมูล
try:
    print(f"Loading dataset: {dataset_name}")
    # ใช้ขนาดที่เหมาะสมสำหรับการทดสอบ
    train_dataset = load_dataset(dataset_name, split="train[:5%]")  # ลดเป็น 5% เพื่อความเร็ว
    val_dataset = load_dataset(dataset_name, split="validation[:100]")  # ใช้ validation set น้อยลง
    print(f"Training dataset loaded: {len(train_dataset)} samples")
    print(f"Validation dataset loaded: {len(val_dataset)} samples")
except Exception as e:
    print(f"Error loading dataset {dataset_name}: {e}")
    # ใช้ dummy Thai dataset สำหรับทดสอบ
    print("Creating dummy Thai dataset for testing...")
    from datasets import Dataset
    dummy_data = {
        "body": [
            "นักวิทยาศาสตร์ได้พัฒนาเทคโนโลยีปัญญาประดิษฐ์ใหม่ที่สามารถช่วยในการวินิจฉัยโรคได้อย่างแม่นยำ โดยใช้การเรียนรู้เชิงลึกในการวิเคราะห์ภาพถ่ายทางการแพทย์",
            "รัฐบาลได้ประกาศนโยบายใหม่เพื่อส่งเสริมการใช้พลังงานทดแทน โดยเฉพาะพลังงานแสงอาทิตย์และพลังงานลม เพื่อลดการปล่อยก๊าซเรือนกระจก",
            "การศึกษาใหม่พบว่าการออกกำลังกายสม่ำเสมอไม่เพียงแต่ช่วยให้ร่างกายแข็งแรง แต่ยังช่วยปรับปรุงสุขภาพจิตและลดความเครียดได้อีกด้วย"
        ] * 4,  # 12 samples total
        "summary": [
            "นักวิทยาศาสตร์พัฒนา AI ใหม่สำหรับวินิจฉัยโรคด้วยการเรียนรู้เชิงลึก",
            "รัฐบาลส่งเสริมพลังงานทดแทนเพื่อลดก๊าซเรือนกระจก",
            "การออกกำลังกายช่วยทั้งร่างกายและจิตใจ ลดความเครียด"
        ] * 4
    }
    train_dataset = Dataset.from_dict(dummy_data)
    val_dataset = Dataset.from_dict(dummy_data)

def preprocess(sample):
    # ใช้โครงสร้างของ pythainlp/thaisum dataset
    if "body" in sample and "summary" in sample:
        # ใช้ body (เนื้อหาข่าว) เป็น article สำหรับการสรุป
        article_text = sample["body"]
        summary_text = sample["summary"]
        
        # สร้าง prompt สำหรับการเรียนรู้การสรุปภาษาไทย
        prompt = f"สรุปข่าวต่อไปนี้:\n\n{article_text}\n\nสรุป:"
        full_text = prompt + summary_text + tokenizer.eos_token
        return {"text": full_text}
    elif "article" in sample and "summary" in sample:
        # Fallback สำหรับ format เก่า
        prompt = f"สรุปใจความสำคัญของบทความต่อไปนี้เป็นภาษาไทย:\n{sample['article']}\nสรุป:"
        full_text = prompt + sample["summary"] + tokenizer.eos_token
        return {"text": full_text}
    else:
        # Fallback สำหรับ DialoGPT หรือโมเดลอื่น
        full_text = f"Human: Hello\nBot: Hi there!{tokenizer.eos_token}"
        return {"text": full_text}

train_dataset = train_dataset.map(preprocess)
val_dataset = val_dataset.map(preprocess)
print(f"Training dataset preprocessed: {len(train_dataset)} samples")
print(f"Validation dataset preprocessed: {len(val_dataset)} samples")

# ตั้งค่าการเทรน
output_dir = "./qwen_thai_lora" if "Qwen" in model_name else "./dialogpt_lora"

# ตรวจสอบ GPU และ precision
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
use_fp16 = torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 7
use_bf16 = torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8

print(f"Device: {device}")
print(f"FP16 support: {use_fp16}")
print(f"BF16 support: {use_bf16}")

# ฟังก์ชันสำหรับคำนวณ ROUGE scores
def compute_rouge_scores(predictions, references):
    """คำนวณ ROUGE scores สำหรับการประเมิน summarization"""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=False)
    
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    
    for pred, ref in zip(predictions, references):
        # ทำความสะอาดข้อความ
        pred_clean = pred.strip() if pred else ""
        ref_clean = ref.strip() if ref else ""
        
        if pred_clean and ref_clean:
            scores = scorer.score(ref_clean, pred_clean)
            rouge1_scores.append(scores['rouge1'].fmeasure)
            rouge2_scores.append(scores['rouge2'].fmeasure)
            rougeL_scores.append(scores['rougeL'].fmeasure)
        else:
            rouge1_scores.append(0.0)
            rouge2_scores.append(0.0)
            rougeL_scores.append(0.0)
    
    return {
        'rouge1': np.mean(rouge1_scores),
        'rouge2': np.mean(rouge2_scores),
        'rougeL': np.mean(rougeL_scores)
    }

def compute_metrics(eval_preds):
    """ฟังก์ชันสำหรับคำนวณ metrics ใน training loop"""
    # สำหรับ SFTTrainer เราจะทำ evaluation แยกต่างหาก
    return {}

def evaluate_model_rouge(model, tokenizer, eval_samples):
    """ประเมินโมเดลด้วย ROUGE scores"""
    print("Generating predictions for ROUGE evaluation...")
    
    predictions = []
    references = []
    
    model.eval()
    with torch.no_grad():
        for i, sample in enumerate(eval_samples):
            if i % 10 == 0:
                print(f"Processing sample {i+1}/{len(eval_samples)}")
            
            # สร้าง prompt
            if "body" in sample and "summary" in sample:
                article = sample["body"]
                reference = sample["summary"]
                prompt = f"สรุปข่าวต่อไปนี้:\n\n{article}\n\nสรุป:"
            else:
                continue
                
            # Tokenize และ generate
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=400)
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            try:
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id,
                    no_repeat_ngram_size=2
                )
                
                # Decode และแยกเฉพาะส่วน summary
                generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
                if "สรุป:" in generated:
                    prediction = generated.split("สรุป:")[-1].strip()
                else:
                    prediction = generated.strip()
                
                predictions.append(prediction)
                references.append(reference)
                
            except Exception as e:
                print(f"Error generating for sample {i}: {e}")
                predictions.append("")
                references.append(reference)
    
    # คำนวณ ROUGE scores
    if predictions and references:
        rouge_results = compute_rouge_scores(predictions, references)
        
        print("\n" + "="*60)
        print("🔍 ROUGE Evaluation Results:")
        print("="*60)
        print(f"ROUGE-1: {rouge_results['rouge1']:.4f}")
        print(f"ROUGE-2: {rouge_results['rouge2']:.4f}")
        print(f"ROUGE-L: {rouge_results['rougeL']:.4f}")
        print("="*60)
        
        # บันทึกผลลัพธ์
        with open(f"{output_dir}/rouge_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "rouge_scores": rouge_results,
                "num_samples": len(predictions),
                "sample_predictions": predictions[:5],  # เก็บตัวอย่าง 5 ข้อแรก
                "sample_references": references[:5]
            }, f, ensure_ascii=False, indent=2)
        
        return rouge_results
    else:
        print("No predictions generated for evaluation")
        return None

training_args = TrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=1,  # ลด batch size เพื่อประหยัด memory
    per_device_eval_batch_size=1,   # ลด eval batch size
    gradient_accumulation_steps=8,  # เพิ่มเพื่อชดเชย batch size ที่เล็กลง
    num_train_epochs=2,
    learning_rate=2e-4,
    warmup_steps=50,
    fp16=use_fp16 and not use_bf16,
    bf16=use_bf16,
    logging_steps=50,    # logging ไม่บ่อยเกินไป
    eval_steps=200,      # evaluate น้อยลงเพื่อประหยัด memory
    eval_strategy="steps",
    save_strategy="steps",
    save_steps=200,
    save_total_limit=1,  # เก็บไว้แค่ 1 checkpoint
    load_best_model_at_end=False,  # ปิดเพื่อประหยัด memory
    remove_unused_columns=False,
    report_to=None,
    dataloader_num_workers=0,
    max_steps=300,  # ลดจำนวน steps
    dataloader_pin_memory=False,  # ประหยัด memory
    eval_accumulation_steps=1,  # ประหยัด memory ตอน evaluation
)

# เทรนด้วย SFTTrainer (supervised fine-tune)
try:
    print("Creating SFTTrainer...")
    # ใช้ API ที่ถูกต้องสำหรับ TRL v0.23.1
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,  # เพิ่ม validation dataset
        args=training_args,
        compute_metrics=compute_metrics,
    )
    
    print("Starting training...")
    trainer.train()
    
    print("Evaluating model with ROUGE scores...")
    # ทำ evaluation บน validation set
    evaluate_model_rouge(model, tokenizer, val_dataset[:20])  # ทดสอบ 20 samples เพื่อความเร็ว
    
    print("Saving model...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Model saved to {output_dir}")
    
except Exception as e:
    print(f"Training error: {e}")
    import traceback
    traceback.print_exc()
    
    # บันทึกโมเดลแม้เกิดข้อผิดพลาด
    try:
        print("Attempting to save model anyway...")
        model.save_pretrained(output_dir + "_partial")
        tokenizer.save_pretrained(output_dir + "_partial")
        print(f"Partial model saved to {output_dir}_partial")
    except Exception as save_e:
        print(f"Could not save model: {save_e}")

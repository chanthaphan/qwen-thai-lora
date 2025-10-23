#!/usr/bin/env python3
"""
Module 2.2: Model Training & Fine-tuning
=======================================

Interactive learning script to master model training pipelines and fine-tuning techniques.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎓 {title}")
    print(f"{'='*60}\n")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"📚 Step {step_num}: {description}")
    print("-" * 40)

def explain_training_pipeline():
    """Explain the model training pipeline."""
    print("""
🔄 Model Training Pipeline Overview:

1. 📊 Data Preparation
   • Load and preprocess Thai text data
   • Tokenization and sequence formatting
   • Train/validation/test split
   • Data collation and batching

2. 🏗️ Model Setup
   • Load base model (Qwen2.5-1.5B-Instruct)
   • Apply LoRA adapters to target modules
   • Configure gradient checkpointing for memory efficiency
   • Set up mixed precision training (fp16/bf16)

3. ⚙️ Training Configuration
   • Learning rate scheduling (linear warmup)
   • Optimization (AdamW with paging)
   • Gradient accumulation and clipping
   • Evaluation strategy and metrics

4. 🚀 Training Loop
   • Forward pass with teacher forcing
   • Loss computation (cross-entropy)
   • Backward pass with gradient accumulation
   • Parameter updates and logging

5. 📈 Evaluation & Monitoring
   • Perplexity and BLEU score tracking
   • Loss curves and learning rate plots
   • Model checkpointing and early stopping
   • Validation on held-out data
""")

def explain_lora_training():
    """Explain LoRA training specifics."""
    print("""
🎯 LoRA Training Deep Dive:

💡 Key Concepts:
   • Only LoRA parameters are trainable (~0.1% of total)
   • Base model remains frozen throughout training
   • Multiple LoRA adapters can be trained for different tasks
   • Adapters can be merged back into base model

⚙️ Critical Parameters:
   
   📐 Rank (r): 4, 8, 16, 32
      • Higher rank = more parameters but better expressiveness
      • Thai language typically works well with r=16
   
   🔢 Alpha (α): Usually 2×r (e.g., α=32 for r=16)
      • Controls the scaling of LoRA updates
      • Higher alpha = stronger adaptation
   
   🎯 Target Modules: ["q_proj", "v_proj", "k_proj", "o_proj"]
      • Which attention layers to apply LoRA to
      • Can also include MLP layers: ["gate_proj", "up_proj", "down_proj"]
   
   💧 Dropout: 0.05 - 0.1
      • Regularization for LoRA layers only
      • Prevents overfitting to training data

🔄 Training Process:
   1. Base model forward pass (frozen parameters)
   2. LoRA forward pass: h = h + BA × input
   3. Loss computation on combined output
   4. Gradients only flow through LoRA parameters
   5. Update only A and B matrices

📊 Memory Benefits:
   • Full fine-tuning: ~6GB VRAM for 1.5B model
   • LoRA training: ~2-3GB VRAM for same model
   • Enables training on consumer GPUs
""")

def demonstrate_training_config():
    """Demonstrate training configuration."""
    print("""
🛠️ Training Configuration Breakdown:

📋 Essential Training Arguments:
""")
    
    # Show actual training config
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config" / "training_config.yaml"
    
    if config_path.exists():
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            print("🔧 Current Training Configuration:")
            
            # Show key sections with explanations
            sections = {
                'lora': '🎯 LoRA Configuration',
                'training': '📈 Training Parameters', 
                'dataset': '📊 Dataset Settings',
                'evaluation': '🧪 Evaluation Strategy',
                'logging': '📝 Logging & Checkpointing'
            }
            
            for section, title in sections.items():
                if section in config:
                    print(f"\n{title}:")
                    for key, value in config[section].items():
                        print(f"  • {key}: {value}")
                        
                        # Add explanations for key parameters
                        explanations = {
                            'r': 'LoRA rank - higher = more parameters',
                            'alpha': 'LoRA scaling factor - typically 2×rank',
                            'learning_rate': 'Step size for parameter updates',
                            'per_device_train_batch_size': 'Samples per GPU per step',
                            'gradient_accumulation_steps': 'Steps before parameter update',
                            'max_seq_length': 'Maximum input sequence length',
                            'eval_steps': 'Frequency of evaluation runs'
                        }
                        
                        if key in explanations:
                            print(f"    └─ {explanations[key]}")
            
        except Exception as e:
            print(f"❌ Error reading config: {e}")
    else:
        print("❌ Training config file not found")

def show_dataset_preparation():
    """Show dataset preparation concepts."""
    print("""
📊 Thai Dataset Preparation:

🌍 Thai Language Challenges:
   • No word boundaries: "ฉันไปโรงเรียน" (I go to school)
   • Complex script with tone marks and vowel positions
   • Mixed script: Thai + English + numbers
   • Formal vs informal language styles

📝 Data Preprocessing Pipeline:

1. 🧹 Text Cleaning:
   ```python
   def clean_thai_text(text):
       # Remove excessive whitespace
       text = re.sub(r'\s+', ' ', text)
       # Normalize Thai characters
       text = unicodedata.normalize('NFKC', text)
       # Remove special characters but keep Thai punctuation
       return text.strip()
   ```

2. 🔤 Tokenization Strategy:
   ```python
   # Using Qwen tokenizer for Thai
   tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
   
   # Example Thai text
   text = "สวัสดีครับ ผมเป็นโมเดลภาษาไทย"
   tokens = tokenizer.encode(text)
   
   # Check token efficiency
   compression_ratio = len(text) / len(tokens)
   print(f"Compression: {compression_ratio:.2f} chars per token")
   ```

3. 📏 Sequence Formatting:
   ```python
   def format_chat_template(conversation):
       formatted = tokenizer.apply_chat_template(
           conversation,
           tokenize=False,
           add_generation_prompt=False
       )
       return formatted
   
   # Example conversation
   conversation = [
       {"role": "user", "content": "อธิบายเรื่อง AI"},
       {"role": "assistant", "content": "AI หรือปัญญาประดิษฐ์..."}
   ]
   ```

📈 Data Augmentation Techniques:
   • Back-translation (Thai → English → Thai)
   • Paraphrasing with existing models
   • Synthetic data generation
   • Code-switching examples (Thai-English mix)
""")

def explain_evaluation_metrics():
    """Explain model evaluation metrics."""
    print("""
📏 Model Evaluation Metrics:

🎯 Language Generation Metrics:

1. 📉 Perplexity (PPL):
   • Measures how "surprised" the model is by test data
   • Lower is better: PPL = exp(cross_entropy_loss)
   • Good Thai models: PPL < 10-15

2. 🎨 BLEU Score (0-100):
   • Compares generated text to reference translations
   • Measures n-gram overlap precision
   • Good for translation tasks: BLEU > 20-30

3. 🔍 ROUGE Scores:
   • ROUGE-L: Longest common subsequence
   • Good for summarization: ROUGE-L > 0.3-0.4

4. 🧠 Semantic Similarity:
   • Embedding-based similarity (cosine distance)
   • Captures meaning beyond surface form
   • Use multilingual embeddings for Thai

💡 Thai-Specific Evaluation:

1. 📝 Word Segmentation Quality:
   ```python
   # Test if model maintains proper Thai word boundaries
   input_text = "ฉันไปโรงเรียน"
   output_text = model.generate(input_text)
   
   # Check if output preserves linguistic structure
   ```

2. 🎭 Politeness Level Consistency:
   • Thai has multiple politeness levels (กรุณา, ขอ, ครับ/ค่ะ)
   • Model should maintain consistent register
   • Evaluate across formal/informal contexts

3. 🌐 Code-Switching Handling:
   • Thai-English mixed sentences
   • Technical terms in English within Thai context
   • Proper script switching

📊 Automated Evaluation Setup:
   ```python
   def evaluate_thai_model(model, eval_dataset):
       results = {
           'perplexity': [],
           'bleu_scores': [],
           'rouge_scores': [],
           'generation_examples': []
       }
       
       for batch in eval_dataset:
           # Compute perplexity
           with torch.no_grad():
               outputs = model(**batch)
               ppl = torch.exp(outputs.loss)
               results['perplexity'].append(ppl.item())
           
           # Generate and evaluate BLEU
           generated = model.generate(batch['input_ids'])
           bleu = compute_bleu(generated, batch['labels'])
           results['bleu_scores'].append(bleu)
       
       return results
   ```
""")

def main():
    print_header("Module 2.2: Model Training & Fine-tuning")
    
    project_root = Path(__file__).parent.parent
    
    # Step 1: Training Pipeline Overview
    print_step(1, "Understanding the Training Pipeline")
    explain_training_pipeline()
    
    input("\n🔍 Press Enter to learn about LoRA training...")
    
    # Step 2: LoRA Training Deep Dive
    print_step(2, "LoRA Training Deep Dive")
    explain_lora_training()
    
    input("\n🔍 Press Enter to explore training configuration...")
    
    # Step 3: Training Configuration
    print_step(3, "Training Configuration Analysis")
    demonstrate_training_config()
    
    input("\n🔍 Press Enter to learn about dataset preparation...")
    
    # Step 4: Dataset Preparation
    print_step(4, "Thai Dataset Preparation")
    show_dataset_preparation()
    
    input("\n🔍 Press Enter to learn about evaluation...")
    
    # Step 5: Evaluation Metrics
    print_step(5, "Model Evaluation Metrics")
    explain_evaluation_metrics()
    
    input("\n🔍 Press Enter to see practical exercises...")
    
    # Step 6: Practical Exercises
    print_step(6, "Practical Training Exercises")
    
    print("""
🧪 Hands-on Training Experiments:

1. 📊 Analyze Your Training Data:
   ```python
   # Explore the training configuration
   import yaml
   with open('config/training_config.yaml', 'r') as f:
       config = yaml.safe_load(f)
   
   print("LoRA Config:", config['lora'])
   print("Batch Size:", config['training']['per_device_train_batch_size'])
   print("Learning Rate:", config['training']['learning_rate'])
   ```

2. 🔧 Calculate Training Parameters:
   ```python
   # Estimate training time and memory
   def estimate_training_resources(config):
       batch_size = config['training']['per_device_train_batch_size']
       grad_accum = config['training']['gradient_accumulation_steps']
       effective_batch = batch_size * grad_accum
       
       print(f"Effective batch size: {effective_batch}")
       print(f"LoRA rank: {config['lora']['r']}")
       
       # Estimate parameters
       base_params = 1.5e9  # 1.5B model
       lora_params = estimate_lora_params(config['lora'])
       print(f"LoRA parameters: {lora_params:,.0f} ({lora_params/base_params*100:.3f}% of base)")
   ```

3. 🎯 Experiment with LoRA Settings:
   ```python
   # Try different LoRA configurations
   lora_experiments = [
       {'r': 8, 'alpha': 16},   # Small, fast
       {'r': 16, 'alpha': 32},  # Balanced (current)
       {'r': 32, 'alpha': 64},  # Large, expressive
   ]
   
   for config in lora_experiments:
       params = 2 * config['r'] * 4096  # Approximate for attention layers
       print(f"Rank {config['r']}: ~{params:,.0f} parameters")
   ```

4. 📈 Monitor Training Progress:
   ```bash
   # If you have a trained model, examine the logs
   ls -la models/qwen_thai_lora/
   
   # Look for training logs and checkpoints
   find models/ -name "*.log" -o -name "trainer_state.json"
   ```

5. 🧮 Evaluate Model Performance:
   ```python
   # Load and test a checkpoint
   from transformers import AutoTokenizer
   from peft import PeftModel
   
   # Load base model and adapter
   base_model = "Qwen/Qwen2.5-1.5B-Instruct"
   adapter_path = "models/qwen_thai_lora"
   
   tokenizer = AutoTokenizer.from_pretrained(base_model)
   
   # Test Thai generation
   prompt = "อธิบายเรื่องปัญญาประดิษฐ์"
   inputs = tokenizer(prompt, return_tensors="pt")
   
   # Compare with base model vs fine-tuned model
   ```

📚 Advanced Training Topics to Explore:

🔬 Hyperparameter Tuning:
   • Learning rate scheduling strategies
   • Batch size vs convergence speed trade-offs
   • Gradient accumulation for memory constraints
   • Early stopping criteria

📊 Data Quality & Augmentation:
   • Creating high-quality Thai instruction datasets
   • Balancing formal vs informal language
   • Handling domain-specific terminology
   • Quality filtering techniques

🎯 Specialized Fine-tuning:
   • Task-specific adapters (summarization, QA, chat)
   • Multi-task learning with shared base
   • Instruction tuning vs chat fine-tuning
   • Constitutional AI principles

⚡ Optimization Techniques:
   • Gradient checkpointing for memory efficiency
   • Mixed precision training (fp16/bf16)
   • DeepSpeed integration for large models
   • Model parallelism strategies

🎯 Key Takeaways:
   • LoRA enables efficient fine-tuning with minimal resources
   • Thai language requires special tokenization considerations
   • Proper evaluation metrics are crucial for Thai models
   • Training configuration significantly impacts results

🚀 Ready for Module 3.1: FastAPI Fundamentals!
""")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Module 2.1: Understanding Transformers & LoRA
============================================

Interactive learning script to understand transformer architecture and LoRA fine-tuning.
"""

import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎓 {title}")
    print(f"{'='*60}\n")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"📚 Step {step_num}: {description}")
    print("-" * 40)

def explain_transformer_architecture():
    """Explain transformer architecture concepts."""
    print("""
🧠 Transformer Architecture Overview:

1. 🔤 Input Embedding Layer
   • Converts tokens to dense vectors
   • Position encoding adds sequence information

2. 🎯 Multi-Head Attention Mechanism
   • Query (Q), Key (K), Value (V) matrices
   • Attention(Q,K,V) = softmax(QK^T/√d_k)V
   • Multiple attention heads capture different relationships

3. 🔄 Feed-Forward Networks
   • Two linear transformations with ReLU activation
   • FFN(x) = max(0, xW1 + b1)W2 + b2

4. 🏗️ Layer Normalization & Residual Connections
   • LayerNorm(x + Sublayer(x))
   • Helps with gradient flow and training stability

5. 📤 Output Layer
   • Linear layer projects to vocabulary size
   • Softmax for probability distribution over tokens
""")

def explain_attention_mechanism():
    """Explain attention mechanism in detail."""
    print("""
🎯 Self-Attention Mechanism Deep Dive:

💡 The Intuition:
   When processing "The cat sat on the mat", for the word "sat":
   • Query: "What am I looking for?"
   • Key: "What can be attended to?"
   • Value: "What information to extract?"

🔢 The Math:
   1. Create Q, K, V matrices from input embeddings
   2. Compute attention scores: scores = Q × K^T
   3. Scale by √d_k to prevent vanishing gradients
   4. Apply softmax to get attention weights
   5. Multiply by V to get weighted representations

🌟 Why It Works:
   • Captures long-range dependencies
   • Parallel computation (unlike RNNs)
   • Different heads focus on different relationships
   • Position-independent but position-aware
""")

def explain_lora():
    """Explain LoRA (Low-Rank Adaptation) technique."""
    print("""
🚀 LoRA (Low-Rank Adaptation) Explained:

❓ The Problem:
   • Full fine-tuning requires updating ALL parameters
   • Qwen2.5-1.5B has ~1.5 billion parameters
   • Memory and compute intensive

💡 The LoRA Solution:
   Instead of updating W → W + ΔW where ΔW is full rank,
   LoRA approximates: ΔW ≈ A × B
   
   Where:
   • A has shape (d, r) 
   • B has shape (r, d)
   • r << d (rank is much smaller than dimension)

🔢 The Math:
   Original: h = Wx
   With LoRA: h = Wx + ΔWx = Wx + BAx
   
   Parameters:
   • Original: d × d parameters
   • LoRA: d × r + r × d = 2dr parameters
   • If d=4096, r=16: 16M vs 0.13M parameters! (99.2% reduction)

⚙️ Key Parameters:
   • r (rank): Higher = more expressive but more parameters
   • α (alpha): Scaling factor, typically 2×r
   • Target modules: Which layers to apply LoRA to
   • Dropout: Regularization for LoRA layers

🎯 Benefits:
   • 99%+ parameter reduction
   • Faster training and inference
   • Multiple adapters can be swapped
   • Original model stays frozen
""")

def demonstrate_tokenization():
    """Demonstrate Thai tokenization concepts."""
    print("""
🔤 Thai Language Tokenization Challenges:

🌍 Thai Language Characteristics:
   • No spaces between words: "ฉันรักประเทศไทย"
   • Complex script with vowels above/below consonants
   • Compound words and Sanskrit loanwords
   • Context-dependent word boundaries

🛠️ Tokenization Strategies:

1. 📝 Character-level:
   "สวัสดี" → ['ส', 'ว', 'ั', 'ส', 'ด', 'ี']
   + Handles any text
   - Long sequences, loses word meaning

2. 🔤 Subword (BPE/SentencePiece):
   "สวัสดี" → ['สวัส', 'ดี'] or ['ส', 'วัสดี']
   + Balance between coverage and meaning
   + Handles rare words

3. 📖 Word-level:
   "ฉันรักไทย" → ['ฉัน', 'รัก', 'ไทย'] (requires word segmentation)
   + Preserves semantic meaning
   - Vocabulary explosion, OOV issues

🎯 Modern Approach (Qwen2.5):
   Uses SentencePiece with vocabulary of ~150K tokens
   Trained on multilingual data including Thai
""")

def main():
    print_header("Module 2.1: Understanding Transformers & LoRA")
    
    project_root = Path(__file__).parent.parent
    
    # Step 1: Transformer Architecture
    print_step(1, "Transformer Architecture Fundamentals")
    explain_transformer_architecture()
    
    input("\n🔍 Press Enter to learn about attention mechanism...")
    
    # Step 2: Attention Mechanism
    print_step(2, "Self-Attention Mechanism")
    explain_attention_mechanism()
    
    input("\n🔍 Press Enter to learn about LoRA...")
    
    # Step 3: LoRA Technique
    print_step(3, "LoRA (Low-Rank Adaptation)")
    explain_lora()
    
    input("\n🔍 Press Enter to learn about tokenization...")
    
    # Step 4: Thai Tokenization
    print_step(4, "Thai Language Tokenization")
    demonstrate_tokenization()
    
    input("\n🔍 Press Enter to explore the model code...")
    
    # Step 5: Exploring Model Code
    print_step(5, "Exploring Thai Model Implementation")
    
    try:
        sys.path.insert(0, str(project_root))
        
        # Show model structure
        model_file = project_root / "thai_model" / "core" / "model.py"
        if model_file.exists():
            print(f"📄 Examining {model_file}:")
            
            with open(model_file, 'r') as f:
                lines = f.readlines()
            
            # Show class structure
            in_class = False
            indent_level = 0
            for i, line in enumerate(lines[:50]):  # First 50 lines
                if 'class ThaiModel' in line:
                    in_class = True
                    indent_level = len(line) - len(line.lstrip())
                    print(f"Line {i+1:2}: {line.rstrip()}")
                elif in_class:
                    if line.strip() and len(line) - len(line.lstrip()) <= indent_level:
                        break
                    if 'def ' in line or '__init__' in line:
                        print(f"Line {i+1:2}: {line.rstrip()}")
        
        # Try to show config structure
        config_file = project_root / "thai_model" / "core" / "config.py"
        if config_file.exists():
            print(f"\n📄 ModelConfig structure:")
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Extract ModelConfig class
            if '@dataclass' in content and 'class ModelConfig' in content:
                lines = content.split('\n')
                in_modelconfig = False
                for line in lines:
                    if 'class ModelConfig' in line:
                        in_modelconfig = True
                        print(f"  {line.strip()}")
                    elif in_modelconfig and line.strip().startswith(('model_', 'max_', 'temperature', 'device')):
                        print(f"  {line.strip()}")
                    elif in_modelconfig and line.strip() and not line.startswith('    '):
                        break
    
    except Exception as e:
        print(f"❌ Error exploring code: {e}")
        print("💡 The model files are available for manual inspection")
    
    input("\n🔍 Press Enter to see practical examples...")
    
    # Step 6: Practical Examples
    print_step(6, "Practical Examples & Next Steps")
    
    print("""
🧪 Hands-on Experiments You Can Try:

1. 🔍 Explore Model Architecture:
   ```python
   from transformers import AutoModel
   model = AutoModel.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
   print(model)  # See the full architecture
   ```

2. 🔤 Experiment with Tokenization:
   ```python
   from transformers import AutoTokenizer
   tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
   
   text = "สวัสดีครับ ผมชื่อ AI"
   tokens = tokenizer.encode(text)
   print(f"Tokens: {tokens}")
   print(f"Decoded: {tokenizer.decode(tokens)}")
   ```

3. ⚙️ Examine LoRA Configuration:
   ```python
   from peft import LoraConfig
   
   lora_config = LoraConfig(
       r=16,                    # Rank
       lora_alpha=32,          # Alpha scaling
       target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
       lora_dropout=0.1,       # Dropout
   )
   print(lora_config)
   ```

4. 📊 Check Model Parameters:
   ```python
   def count_parameters(model):
       return sum(p.numel() for p in model.parameters() if p.requires_grad)
   
   # Compare base model vs LoRA model parameter counts
   ```

📚 Study Materials for Deep Dive:
  • "Attention Is All You Need" paper (Vaswani et al.)
  • "LoRA: Low-Rank Adaptation" paper (Hu et al.)
  • Hugging Face Transformers documentation
  • Thai NLP resources and datasets

🎯 Key Takeaways:
  • Transformers use self-attention for sequence modeling
  • LoRA enables efficient fine-tuning with minimal parameters
  • Thai requires special tokenization considerations
  • The thai_model package wraps these concepts cleanly

🚀 Ready for Module 2.2: Model Training & Fine-tuning!
""")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Thai Model Web Interface using Gradio
Host your fine-tuned Thai model with a user-friendly web GUI
"""

import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import sys
from pathlib import Path

class ThaiModelInterface:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        
    def load_model(self):
        """Load the fine-tuned Thai model"""
        try:
            base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
            lora_model_path = "./models/qwen_thai_lora"
            
            if not Path(lora_model_path).exists():
                return False, "❌ Model not found at ./models/qwen_thai_lora. Please train the model first."
            
            print("Loading Thai model...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
            
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            
            # Load LoRA adapter
            self.model = PeftModel.from_pretrained(base_model, lora_model_path)
            self.model.eval()
            
            self.model_loaded = True
            return True, "✅ Thai model loaded successfully!"
            
        except Exception as e:
            return False, f"❌ Error loading model: {e}"
    
    def generate_thai_summary(self, text, max_length=150, temperature=0.7):
        """Generate Thai summary for the input text"""
        if not self.model_loaded:
            success, message = self.load_model()
            if not success:
                return message
        
        try:
            # Create Thai summarization prompt
            prompt = f"สรุปข่าวต่อไปนี้:\n\n{text}\n\nสรุป:"
            
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=450)
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    do_sample=True,
                    temperature=temperature,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3
                )
            
            # Decode and extract summary
            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the summary part
            if "สรุป:" in generated:
                summary = generated.split("สรุป:")[-1].strip()
            else:
                summary = generated.strip()
            
            return summary
            
        except Exception as e:
            return f"❌ Error generating summary: {e}"
    
    def chat_with_model(self, message, history, max_length, temperature):
        """Chat interface for the model"""
        if not message.strip():
            return "", history
        
        # Generate response
        response = self.generate_thai_summary(message, max_length, temperature)
        
        # Add to history
        history.append((message, response))
        
        return "", history

def create_interface():
    """Create Gradio interface"""
    
    thai_model = ThaiModelInterface()
    
    # Custom CSS
    css = """
    .gradio-container {
        max-width: 1000px;
        margin: auto;
    }
    .thai-text {
        font-family: 'Sarabun', 'Noto Sans Thai', sans-serif;
        font-size: 16px;
    }
    """
    
    with gr.Blocks(css=css, title="Thai Model Interface") as demo:
        gr.Markdown("""
        # 🇹🇭 Thai Language Model Interface
        ## Fine-tuned Qwen2.5 with LoRA for Thai Text Summarization
        
        This interface uses your locally trained Thai model to generate summaries and responses in Thai language.
        """)
        
        with gr.Tab("📝 Thai Summarization"):
            with gr.Row():
                with gr.Column():
                    input_text = gr.Textbox(
                        lines=8,
                        placeholder="กรุณาใส่ข้อความที่ต้องการสรุปเป็นภาษาไทย...",
                        label="ข้อความต้นฉบับ (Original Text)",
                        elem_classes=["thai-text"]
                    )
                    
                    with gr.Row():
                        summarize_btn = gr.Button("สรุป (Summarize)", variant="primary")
                        clear_btn = gr.Button("ล้าง (Clear)")
                    
                    with gr.Accordion("⚙️ Advanced Settings", open=False):
                        max_length = gr.Slider(
                            minimum=50,
                            maximum=300,
                            value=150,
                            step=10,
                            label="Max Summary Length"
                        )
                        temperature = gr.Slider(
                            minimum=0.1,
                            maximum=1.0,
                            value=0.7,
                            step=0.1,
                            label="Temperature (Creativity)"
                        )
                
                with gr.Column():
                    output_text = gr.Textbox(
                        lines=8,
                        label="สรุป (Summary)",
                        elem_classes=["thai-text"],
                        interactive=False
                    )
                    
                    status_text = gr.Textbox(
                        label="Status",
                        interactive=False,
                        max_lines=2
                    )
        
        with gr.Tab("💬 Chat with Thai Model"):
            chatbot = gr.Chatbot(
                height=500,
                label="Thai Model Chat",
                elem_classes=["thai-text"]
            )
            
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="พิมพ์ข้อความของคุณ...",
                    label="Your Message",
                    scale=4,
                    elem_classes=["thai-text"]
                )
                chat_send = gr.Button("Send", scale=1)
            
            with gr.Row():
                chat_clear = gr.Button("Clear Chat")
                
                with gr.Column(scale=2):
                    chat_max_length = gr.Slider(50, 300, 150, label="Response Length")
                    chat_temperature = gr.Slider(0.1, 1.0, 0.7, label="Temperature")
        
        with gr.Tab("ℹ️ Model Info"):
            gr.Markdown("""
            ### 🔧 Model Details
            - **Base Model**: Qwen2.5-1.5B-Instruct
            - **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
            - **Training Data**: Thai news articles and summaries
            - **Specialization**: Thai text summarization
            
            ### 📊 Performance Notes
            - Optimized for Thai language processing
            - Best performance on news articles and formal text
            - May require longer text for better summarization quality
            
            ### 🎯 Usage Tips
            1. **For summarization**: Provide longer Thai text (news articles, documents)
            2. **For chat**: Ask questions or give instructions in Thai
            3. **Adjust temperature**: Lower (0.1-0.4) for consistent output, higher (0.7-1.0) for creative responses
            4. **Adjust length**: Shorter for concise summaries, longer for detailed responses
            """)
            
            model_status = gr.Textbox(
                label="Model Loading Status",
                value="Model not loaded yet. It will load automatically when you first use it.",
                interactive=False
            )
        
        # Event handlers
        def handle_summarize(text, max_len, temp):
            if not text.strip():
                return "", "⚠️ Please enter text to summarize"
            
            summary = thai_model.generate_thai_summary(text, max_len, temp)
            status = "✅ Summary generated successfully!" if not summary.startswith("❌") else "❌ Error occurred"
            return summary, status
        
        def handle_clear():
            return "", "", "Cleared"
        
        # Connect events
        summarize_btn.click(
            fn=handle_summarize,
            inputs=[input_text, max_length, temperature],
            outputs=[output_text, status_text]
        )
        
        clear_btn.click(
            fn=handle_clear,
            outputs=[input_text, output_text, status_text]
        )
        
        # Chat events
        chat_send.click(
            fn=thai_model.chat_with_model,
            inputs=[chat_input, chatbot, chat_max_length, chat_temperature],
            outputs=[chat_input, chatbot]
        )
        
        chat_input.submit(
            fn=thai_model.chat_with_model,
            inputs=[chat_input, chatbot, chat_max_length, chat_temperature],
            outputs=[chat_input, chatbot]
        )
        
        chat_clear.click(
            fn=lambda: ([], "Chat cleared"),
            outputs=[chatbot, model_status]
        )
    
    return demo

def main():
    """Main function"""
    print("🚀 Starting Thai Model Web Interface...")
    
    # Check if model exists
    model_path = Path("./models/qwen_thai_lora")
    if not model_path.exists():
        print("❌ Thai model not found!")
        print("Please run './manage.sh train' first to train the model.")
        sys.exit(1)
    
    print("📁 Model found at:", model_path)
    
    # Create and launch interface
    demo = create_interface()
    
    print("🌐 Launching web interface...")
    print("💡 Open your browser to interact with your Thai model!")
    print("🔧 Use Ctrl+C to stop the server")
    
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7862,       # Different port from chat_gui.py
        share=False,            # Set to True for public link
        show_error=True,
        inbrowser=True          # Auto-open browser
    )

if __name__ == "__main__":
    main()
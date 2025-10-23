# 🔑 How to Fix OpenAI API Key Error

## ❌ **Current Issue**
You're seeing: "OpenAI client not initialized. Please set OPENAI_API_KEY environment variable."

This means you need to set up your OpenAI API key to use GPT models.

## 🚀 **Quick Fix - Choose One:**

### **Option 1: Use the Setup Script (Recommended)**
```bash
./manage.sh setup-openai
```
This will guide you through the setup process step by step.

### **Option 2: Manual Setup**
1. **Get your API key** from: https://platform.openai.com/api-keys
2. **Set the environment variable**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. **Restart the web interface**:
   ```bash
   ./manage.sh chat-web
   ```

### **Option 3: Use Other Backends (No API Key Required)**
You can use the other backends without any API keys:
- **Ollama**: Local models (llama3.1:8b, qwen3:8b)
- **vLLM**: Your fine-tuned Thai model

Just select "Ollama" or "vLLM" from the Backend dropdown instead of "OpenAI".

## 🎯 **After Setting Up API Key**

Once your API key is set, you'll have access to:
- ✅ **GPT-4o** (recommended)
- ✅ **GPT-4o-mini** (faster, cheaper)  
- ✅ **GPT-5** (latest model) ⭐
- ✅ **GPT-5-mini** (latest mini model) ⭐
- ✅ **GPT-4** and **GPT-3.5-turbo**

## 🔄 **Steps to Use OpenAI Models:**
1. Set up API key (using method above)
2. Start web interface: `./manage.sh chat-web`
3. Select **"OpenAI"** from Backend dropdown
4. Choose your preferred GPT model
5. Start chatting!

## 💡 **Troubleshooting**
- **Web interface shows better error messages now** with setup instructions
- **API key is masked in terminal** for security
- **You can make the key permanent** by adding to ~/.bashrc
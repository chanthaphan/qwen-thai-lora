# 🔮 OpenAI Integration Guide

## 🎯 **Overview**

Your Thai model project now supports **OpenAI integration**, allowing you to chat with GPT-4, GPT-4o, GPT-3.5-turbo, and other OpenAI models alongside your local Thai model.

## 🚀 **Quick Setup**

### **1. Get OpenAI API Key**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy your API key

### **2. Set Environment Variable**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Add to your shell profile for persistence
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### **3. Install Dependencies**
```bash
# OpenAI package is automatically installed during setup
./manage.sh setup

# Or install manually
llm-env/bin/pip install openai>=1.0.0
```

## 💬 **Using OpenAI Chat**

### **Command Line Interface**
```bash
# Start interactive OpenAI chat
./manage.sh chat-openai

# Direct prompt mode
llm-env/bin/python -m thai_model.interfaces.openai_chat "Explain quantum physics"

# With specific model
llm-env/bin/python -m thai_model.interfaces.openai_chat --model gpt-4o "What is AI?"

# With reasoning mode
llm-env/bin/python -m thai_model.interfaces.openai_chat --reasoning "Complex problem here"
```

### **Interactive Chat Features**
```bash
🤖 OpenAI Chat App - Interactive Mode

You: สวัสดี มีอะไรให้ช่วยไหม
🤖 Bot: สวัสดี! ผมยินดีที่จะช่วยเหลือคุณ มีอะไรที่อยากจะถามหรือต้องการความช่วยเหลือไหมครับ?

# Available commands during chat:
/help         - Show help information
/model gpt-4  - Switch to GPT-4
/models       - List available models
/reasoning    - Toggle reasoning mode
/stream       - Toggle streaming responses
/temp 0.8     - Set temperature (creativity)
/save chat.json - Save conversation
/load chat.json - Load conversation
/quit         - Exit
```

### **Web Interface**
```bash
# Start web interface with OpenAI support
./manage.sh chat-web

# Visit http://localhost:7860
# Select "openai" from Backend dropdown
# Choose your preferred model (gpt-4o, gpt-4, etc.)
```

## 🤖 **Available Models**

### **Recommended Models:**
- **`gpt-4o`** - Latest multimodal model (best performance) ⭐
- **`gpt-4o-mini`** - Faster, cost-effective version ⭐
- **`gpt-4`** - Previous generation GPT-4
- **`gpt-4-turbo`** - GPT-4 with faster response
- **`gpt-3.5-turbo`** - Fast and economical

### **Model Selection:**
```bash
# In interactive mode
/models                    # List available models
/model gpt-4o             # Switch to GPT-4o
/model gpt-4o-mini        # Switch to GPT-4o mini

# Command line
python -m thai_model.interfaces.openai_chat --model gpt-4o "Your question"
```

## ⚙️ **Configuration Options**

### **Environment Variables:**
```bash
export OPENAI_API_KEY="your-key"      # Required
export OPENAI_BASE_URL="custom-url"  # Optional: custom endpoint
export OPENAI_ORG_ID="org-id"        # Optional: organization ID
```

### **Model Parameters:**
- **Temperature**: 0.0-2.0 (creativity level)
- **Max Tokens**: Response length limit
- **Streaming**: Real-time vs batch responses
- **Reasoning**: Step-by-step thinking mode

### **Usage Examples:**
```bash
# High creativity
/temp 1.2

# More focused responses  
/temp 0.3

# Longer responses
/tokens 4000

# Enable reasoning for complex problems
/reasoning
/rmode detailed
```

## 🔗 **Integration Comparison**

| Feature | Local Thai Model | OpenAI GPT-4 | Ollama |
|---------|------------------|---------------|---------|
| **Cost** | Free | Pay-per-use | Free |
| **Privacy** | Complete | Sent to OpenAI | Complete |
| **Thai Language** | Specialized ⭐ | Good | Good |
| **Speed** | Fast | Fast | Medium |
| **Knowledge** | Training cutoff | Recent | Model dependent |
| **Availability** | Local only | Internet required | Local only |

## 💡 **Best Practices**

### **When to Use OpenAI:**
- ✅ Latest information and knowledge
- ✅ Complex reasoning tasks
- ✅ Code generation and debugging
- ✅ English-centric tasks
- ✅ Creative writing

### **When to Use Thai Model:**
- ✅ Thai language tasks
- ✅ Privacy-sensitive content
- ✅ Offline usage
- ✅ Cost-sensitive applications
- ✅ Custom fine-tuned behavior

### **Hybrid Usage:**
```bash
# Start with local Thai model
./manage.sh chat

# Switch to OpenAI for complex tasks
./manage.sh chat-openai

# Use web interface for model comparison
./manage.sh chat-web
```

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. API Key Not Working**
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Test key validity
./manage.sh chat-openai
```

#### **2. Rate Limits**
- OpenAI has usage limits based on your plan
- Upgrade your OpenAI account for higher limits
- Use temperature settings to get better responses with fewer requests

#### **3. Model Not Available**
```bash
# List available models
/models

# Try alternative models
/model gpt-3.5-turbo    # Fallback option
```

#### **4. Connection Issues**
- Check internet connection
- Verify firewall settings
- Try different OpenAI endpoints

## 📊 **Cost Management**

### **Token Usage:**
- **Input tokens**: Your prompts and conversation history
- **Output tokens**: AI responses
- **Reasoning mode**: Uses more tokens (detailed explanations)

### **Cost Optimization:**
```bash
# Use smaller models for simple tasks
/model gpt-3.5-turbo

# Limit response length
/tokens 500

# Clear conversation history periodically
/clear

# Disable reasoning for simple questions
/reasoning  # toggles off
```

### **Model Pricing (approximate):**
- **GPT-4o**: $15/1M input tokens, $60/1M output tokens
- **GPT-4o-mini**: $0.60/1M input tokens, $2.40/1M output tokens  
- **GPT-3.5-turbo**: $3/1M input tokens, $6/1M output tokens

## 🎉 **Getting Started**

### **Step-by-Step:**

1. **Set up API key:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Test connection:**
   ```bash
   ./manage.sh chat-openai
   ```

3. **Try different models:**
   ```bash
   /models
   /model gpt-4o-mini
   ```

4. **Compare with Thai model:**
   ```bash
   # Thai model
   ./manage.sh chat
   
   # OpenAI
   ./manage.sh chat-openai
   
   # Web interface (both)
   ./manage.sh chat-web
   ```

5. **Explore features:**
   - Reasoning mode for complex problems
   - Streaming for real-time responses
   - Save/load conversations
   - Temperature adjustment for creativity

## 🌟 **Summary**

You now have access to:
- **3 backends**: vLLM (Thai model), Ollama, OpenAI
- **Multiple interfaces**: CLI, Web, Direct commands
- **Flexible models**: Local privacy vs Cloud power
- **Rich features**: Reasoning, streaming, conversation management

Choose the right tool for each task and enjoy the best of both local and cloud AI! 🚀

---

**💡 Pro Tip**: Use the web interface (`./manage.sh chat-web`) to easily switch between all three backends and compare responses!
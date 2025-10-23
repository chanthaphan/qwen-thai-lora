#!/usr/bin/env python3
import requests
import os
import json
import sys
from typing import List, Dict

class OllamaChat:
    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model
        self.host = os.environ.get('OLLAMA_HOST')
        if not self.host:
            print("Error: OLLAMA_HOST environment variable not set")
            print("Please set it with: export OLLAMA_HOST=localhost:11434")
            sys.exit(1)
        
        self.api_url = f"http://{self.host}/api/generate"
        self.conversation_history: List[Dict[str, str]] = []
        self.show_reasoning = False  # Toggle for showing reasoning steps
        self.reasoning_mode = "detailed"  # detailed, simple, or chain
        self.stream_response = True  # Toggle for streaming responses
        
        self.reasoning_prompts = {
            "detailed": """
Think step by step about this question. Show your detailed reasoning process:

**🤔 Analysis:**
1. What is being asked?
2. What information do I need to consider?
3. What are the key points or constraints?

**🧩 Breakdown:**
- Break down the problem into smaller parts
- Consider different approaches or perspectives
- Identify any assumptions I'm making

**⚡ Logic Chain:**
- Step through the reasoning logically
- Show how each step leads to the next
- Consider potential counterarguments or edge cases

**💡 Conclusion:**
[Your final answer with confidence level]

Question: """,
            "simple": """
Show your thinking process briefly:

**🤔 Thinking:** [Quick reasoning steps]
**💡 Answer:** [Your response]

Question: """,
            "chain": """
Use chain-of-thought reasoning. Think through this step-by-step, showing each logical step:

Let me think through this step by step:
Step 1: [First step of reasoning]
Step 2: [Second step of reasoning]
Step 3: [Continue as needed]
Therefore: [Final conclusion]

Question: """
        }
    
    def send_message(self, user_input: str) -> str:
        """Send a message and get response from Ollama"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Build context from conversation history
        if self.show_reasoning:
            # For reasoning mode, prepend the appropriate reasoning prompt
            reasoning_prompt = self.reasoning_prompts.get(self.reasoning_mode, self.reasoning_prompts["detailed"])
            prompt = reasoning_prompt + user_input
        else:
            prompt = self._build_context()
        
        try:
            if self.stream_response:
                return self._send_streaming_message(prompt)
            else:
                return self._send_non_streaming_message(prompt)
                
        except requests.exceptions.RequestException as e:
            return f"Connection error: {e}"
        except KeyError:
            return "Error: Invalid response format from Ollama"
    
    def _send_streaming_message(self, prompt: str) -> str:
        """Send message with streaming response"""
        response = requests.post(
            self.api_url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True
            },
            stream=True,
            timeout=600
        )
        
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code} - {response.text}"
        
        ai_response = ""
        print("🤖 Bot: ", end="", flush=True)
        
        try:
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            token = chunk['response']
                            ai_response += token
                            print(token, end="", flush=True)
                        
                        # Check if this is the final chunk
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
        except KeyboardInterrupt:
            print("\n⚠️ Response interrupted by user")
            ai_response += " [Response interrupted]"
        
        print()  # New line after streaming
        
        # Add AI response to history
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response
    
    def _send_non_streaming_message(self, prompt: str) -> str:
        """Send message without streaming (traditional method)"""
        response = requests.post(
            self.api_url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=600
        )
        
        if response.status_code == 200:
            ai_response = response.json()["response"]
            # Add AI response to history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            return ai_response
        else:
            return f"Error: HTTP {response.status_code} - {response.text}"
    
    def _build_context(self) -> str:
        """Build conversation context from history"""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for msg in self.conversation_history:
            if msg["role"] == "user":
                context_parts.append(f"User: {msg['content']}")
            else:
                context_parts.append(f"Assistant: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def toggle_reasoning(self):
        """Toggle reasoning mode on/off"""
        if not self.show_reasoning:
            # Turn on reasoning - let user choose mode
            print("\n🧠 Select reasoning mode:")
            print("  1. Detailed - Comprehensive step-by-step analysis")
            print("  2. Simple - Brief reasoning with quick steps")
            print("  3. Chain - Chain-of-thought logical progression")
            
            choice = input("Choose mode (1-3) or press Enter for detailed: ").strip()
            
            mode_map = {"1": "detailed", "2": "simple", "3": "chain"}
            self.reasoning_mode = mode_map.get(choice, "detailed")
            self.show_reasoning = True
            
            print(f"✅ Reasoning mode enabled: {self.reasoning_mode}")
            print("   The model will now show its thought process for responses.")
        else:
            # Turn off reasoning
            self.show_reasoning = False
            print("🧠 Reasoning mode disabled!")
            print("   The model will now give direct responses without showing reasoning steps.")
    
    def change_reasoning_mode(self):
        """Change the type of reasoning shown"""
        if not self.show_reasoning:
            print("⚠️  Reasoning mode is currently disabled. Enable it first with /reasoning")
            return
        
        print(f"\n🧠 Current reasoning mode: {self.reasoning_mode}")
        print("Available modes:")
        print("  1. Detailed - Comprehensive step-by-step analysis")
        print("  2. Simple - Brief reasoning with quick steps")
        print("  3. Chain - Chain-of-thought logical progression")
        
        choice = input("Choose new mode (1-3): ").strip()
        mode_map = {"1": "detailed", "2": "simple", "3": "chain"}
        
        if choice in mode_map:
            self.reasoning_mode = mode_map[choice]
            print(f"✅ Reasoning mode changed to: {self.reasoning_mode}")
        else:
            print("❌ Invalid choice. Keeping current mode.")
    
    def toggle_streaming(self):
        """Toggle streaming mode on/off"""
        self.stream_response = not self.stream_response
        status = "enabled" if self.stream_response else "disabled"
        print(f"📡 Streaming mode {status}!")
        if self.stream_response:
            print("   Responses will now appear word-by-word as they're generated.")
        else:
            print("   Responses will now appear all at once after generation is complete.")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("📝 Conversation history cleared!")
    
    def save_conversation(self, filename: str):
        """Save conversation to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            print(f"💾 Conversation saved to {filename}")
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def load_conversation(self, filename: str):
        """Load conversation from a JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            print(f"📂 Conversation loaded from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found")
        except Exception as e:
            print(f"Error loading conversation: {e}")

def print_usage():
    """Print command line usage information"""
    print("🚀 Ollama Chat App")
    print("\nUsage:")
    print("  python3 chat_app.py                              # Interactive chat mode")
    print("  python3 chat_app.py \"your question\"              # Direct answer mode")
    print("  python3 chat_app.py [flags] \"your question\"      # Direct mode with options")
    print("  python3 chat_app.py -h, --help                  # Show this help")
    print("  python3 chat_app.py -v, --version               # Show version")
    print("\nFlags (for direct mode):")
    print("  --reasoning              # Enable step-by-step reasoning")
    print("  --no-stream             # Disable streaming (show complete response)")
    print("  --model MODEL_NAME      # Use specific model")
    print("\nExamples:")
    print("  python3 chat_app.py \"What is Python?\"")
    print("  python3 chat_app.py --reasoning \"Explain quantum computing\"")
    print("  python3 chat_app.py --model llama3.1:70b \"Complex math problem\"")
    print("  python3 chat_app.py --no-stream \"สวัสดี โลก!\"")
    print("  python3 chat_app.py --reasoning --model codellama \"Write a Python function\"")
    print("\nEnvironment:")
    print("  Set OLLAMA_HOST environment variable (e.g., localhost:11434)")
    print("  Make sure Ollama is running with: ollama serve")
    print()

def print_help():
    """Print available commands"""
    print("\n🤖 Chat Commands:")
    print("  /help      - Show this help message")
    print("  /clear     - Clear conversation history")
    print("  /save      - Save conversation to file")
    print("  /load      - Load conversation from file")
    print("  /model     - Change model")
    print("  /reasoning - Toggle reasoning mode (show thought process)")
    print("  /rmode     - Change reasoning mode type (detailed/simple/chain)")
    print("  /stream    - Toggle streaming mode (real-time vs complete responses)")
    print("  /status    - Show current settings")
    print("  /quit      - Exit the chat")
    print()

def handle_direct_prompt(prompt: str):
    """Handle direct prompt from command line arguments"""
    # Parse special flags from the prompt
    args = sys.argv[1:]
    reasoning_mode = False
    no_stream = False
    model_override = None
    
    # Process flags
    filtered_args = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--reasoning':
            reasoning_mode = True
        elif arg == '--no-stream':
            no_stream = True
        elif arg == '--model' and i + 1 < len(args):
            model_override = args[i + 1]
            i += 1  # Skip the next argument (model name)
        else:
            filtered_args.append(arg)
        i += 1
    
    # Rebuild prompt from filtered arguments
    if not filtered_args:
        print("❌ Error: No prompt provided after flags")
        return 1
    
    prompt = " ".join(filtered_args)
    
    print(f"🤖 Ollama Chat - Direct Mode")
    print(f"📝 Prompt: {prompt}")
    if reasoning_mode:
        print("🧠 Reasoning mode: ON")
    if no_stream:
        print("📡 Streaming: OFF")
    if model_override:
        print(f"🔄 Model override: {model_override}")
    print("-" * 50)
    
    # Initialize chat with overrides
    chat = OllamaChat(model=model_override if model_override else "llama3.1:8b")
    
    # Apply mode settings
    if reasoning_mode:
        chat.show_reasoning = True
        chat.reasoning_mode = "simple"  # Use simple mode for CLI
    if no_stream:
        chat.stream_response = False
    
    # Test connection quickly
    try:
        test_response = requests.get(f"http://{chat.host}/api/tags", timeout=3)
        if test_response.status_code != 200:
            print("❌ Cannot connect to Ollama. Make sure it's running with 'ollama serve'")
            return 1
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Ollama. Make sure it's running with 'ollama serve'")
        return 1
    
    print(f"🔗 Connected to Ollama at {chat.host}")
    print(f"🤖 Using model: {chat.model}")
    print()
    
    try:
        # Send the prompt and get response
        if chat.stream_response:
            print("🤖 Response: ", end="", flush=True)
            chat.send_message(prompt)
            print()
        else:
            print("🤖 Generating response...")
            response = chat.send_message(prompt)
            print(f"🤖 Response: {response}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Response interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def main():
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Handle special flags
        if sys.argv[1] in ['-h', '--help']:
            print_usage()
            return 0
        elif sys.argv[1] in ['-v', '--version']:
            print("Ollama Chat App v1.0")
            return 0
        else:
            # Direct prompt mode - answer the question and exit
            prompt = " ".join(sys.argv[1:])
            return handle_direct_prompt(prompt)
    
    print("🚀 Ollama Chat App - Interactive Mode")
    print("💡 Tip: You can also use direct mode: python3 chat_app.py \"your question\"")
    print("Type '/help' for commands or start chatting!")
    print("-" * 50)
    
    # Initialize chat
    chat = OllamaChat()
    
    # Test connection
    print(f"🔗 Connecting to Ollama at {chat.host}...")
    try:
        test_response = requests.get(f"http://{chat.host}/api/tags", timeout=5)
        if test_response.status_code == 200:
            print("✅ Connected to Ollama successfully!")
            available_models = [model['name'] for model in test_response.json().get('models', [])]
            if available_models:
                print(f"📋 Available models: {', '.join(available_models)}")
        else:
            print("⚠️  Ollama server responded but may not be fully ready")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Ollama. Make sure it's running with 'ollama serve'")
        return
    
    print(f"🤖 Using model: {chat.model}")
    reasoning_status = f"ON ({chat.reasoning_mode})" if chat.show_reasoning else "OFF"
    print(f"🧠 Reasoning mode: {reasoning_status}")
    streaming_status = "ON" if chat.stream_response else "OFF"
    print(f"� Streaming mode: {streaming_status}")
    print("�💡 Tip: Use /reasoning for step-by-step thinking, /stream for real-time responses!")
    print("Type your message and press Enter to chat!\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input.lower()
                
                if command == '/quit':
                    print("👋 Goodbye!")
                    break
                elif command == '/help':
                    print_help()
                elif command == '/clear':
                    chat.clear_history()
                elif command.startswith('/save'):
                    filename = input("Enter filename (default: chat_history.json): ").strip()
                    if not filename:
                        filename = "chat_history.json"
                    chat.save_conversation(filename)
                elif command.startswith('/load'):
                    filename = input("Enter filename to load: ").strip()
                    if filename:
                        chat.load_conversation(filename)
                elif command.startswith('/model'):
                    new_model = input(f"Enter model name (current: {chat.model}): ").strip()
                    if new_model:
                        chat.model = new_model
                        print(f"🔄 Model changed to: {new_model}")
                elif command == '/reasoning':
                    chat.toggle_reasoning()
                elif command == '/rmode':
                    chat.change_reasoning_mode()
                elif command == '/stream':
                    chat.toggle_streaming()
                elif command == '/status':
                    print(f"\n📊 Current Settings:")
                    print(f"   🤖 Model: {chat.model}")
                    reasoning_status = f"ON ({chat.reasoning_mode})" if chat.show_reasoning else "OFF"
                    print(f"   🧠 Reasoning mode: {reasoning_status}")
                    streaming_status = "ON" if chat.stream_response else "OFF"
                    print(f"   📡 Streaming mode: {streaming_status}")
                    print(f"   💬 Messages in history: {len(chat.conversation_history)}")
                    print(f"   🔗 Connected to: {chat.host}")
                else:
                    print("❓ Unknown command. Type '/help' for available commands.")
                continue
            
            # Send message to Ollama
            if chat.stream_response:
                # For streaming, the response is printed in real-time
                response = chat.send_message(user_input)
                print()  # Add extra newline after streaming response
            else:
                # For non-streaming, show thinking indicator
                print("🤖 Thinking...", end="", flush=True)
                response = chat.send_message(user_input)
                print(f"\r🤖 Bot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
    
    return 0  # Success

if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        sys.exit(exit_code)
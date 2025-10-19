#!/usr/bin/env python3
"""
vLLM Chat App
A chat application for interacting with vLLM servers using OpenAI-compatible API
"""
import requests
import os
import json
import sys
from typing import List, Dict

class VLLMChat:
    def __init__(self, base_url: str = "http://localhost:8000", model: str = "Qwen/Qwen3-4B-Instruct-2507"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.chat_url = f"{self.base_url}/v1/chat/completions"
        self.models_url = f"{self.base_url}/v1/models"
        self.conversation_history: List[Dict[str, str]] = []
        self.show_reasoning = False
        self.reasoning_mode = "simple"
        self.stream_response = True
        self.max_tokens = 2048
        self.temperature = 0.7
        
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
    
    def test_connection(self) -> str:
        """Test connection to vLLM server"""
        try:
            response = requests.get(self.models_url, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['id'] for model in models_data.get('data', [])]
                return f"✅ Connected to vLLM at {self.base_url}\n📋 Available models: {', '.join(available_models)}"
            else:
                return f"⚠️ vLLM server responded with status {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"❌ Cannot connect to vLLM server: {e}\nMake sure vLLM server is running on {self.base_url}"
    
    def _build_messages(self, user_input: str) -> List[Dict[str, str]]:
        """Build messages array for OpenAI-compatible API"""
        messages = []
        
        # Add conversation history
        for msg in self.conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message with reasoning if enabled
        if self.show_reasoning:
            reasoning_prompt = self.reasoning_prompts.get(self.reasoning_mode, self.reasoning_prompts["simple"])
            content = reasoning_prompt + user_input
        else:
            content = user_input
        
        messages.append({"role": "user", "content": content})
        return messages
    
    def send_message(self, user_input: str) -> str:
        """Send a message and get response from vLLM"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Build messages for API
        messages = self._build_messages(user_input)
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": self.stream_response
        }
        
        try:
            if self.stream_response:
                return self._send_streaming_message(payload)
            else:
                return self._send_non_streaming_message(payload)
        except requests.exceptions.RequestException as e:
            return f"Connection error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    
    def _send_streaming_message(self, payload: dict) -> str:
        """Send message with streaming response"""
        response = requests.post(
            self.chat_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=300
        )
        
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code} - {response.text}"
        
        ai_response = ""
        print("🤖 Bot: ", end="", flush=True)
        
        try:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    token = delta['content']
                                    ai_response += token
                                    print(token, end="", flush=True)
                        except json.JSONDecodeError:
                            continue
        except KeyboardInterrupt:
            print("\n⚠️ Response interrupted by user")
            ai_response += " [Response interrupted]"
        
        print()  # New line after streaming
        
        # Add AI response to history
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response
    
    def _send_non_streaming_message(self, payload: dict) -> str:
        """Send message without streaming"""
        payload["stream"] = False
        response = requests.post(
            self.chat_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                ai_response = response_data['choices'][0]['message']['content']
                # Add AI response to history
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                return ai_response
            else:
                return "Error: No response content received"
        else:
            return f"Error: HTTP {response.status_code} - {response.text}"
    
    def toggle_reasoning(self):
        """Toggle reasoning mode on/off"""
        if not self.show_reasoning:
            # Turn on reasoning - let user choose mode
            print("\n🧠 Select reasoning mode:")
            print("  1. Detailed - Comprehensive step-by-step analysis")
            print("  2. Simple - Brief reasoning with quick steps")
            print("  3. Chain - Chain-of-thought logical progression")
            
            choice = input("Choose mode (1-3) or press Enter for simple: ").strip()
            
            mode_map = {"1": "detailed", "2": "simple", "3": "chain"}
            self.reasoning_mode = mode_map.get(choice, "simple")
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
                json.dump({
                    "model": self.model,
                    "base_url": self.base_url,
                    "conversation": self.conversation_history
                }, f, ensure_ascii=False, indent=2)
            print(f"💾 Conversation saved to {filename}")
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def load_conversation(self, filename: str):
        """Load conversation from a JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.conversation_history = data.get("conversation", [])
            print(f"📂 Conversation loaded from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found")
        except Exception as e:
            print(f"Error loading conversation: {e}")
    
    def change_model(self, new_model: str):
        """Change the model being used"""
        self.model = new_model
        print(f"🔄 Model changed to: {new_model}")
    
    def adjust_settings(self):
        """Adjust temperature and max_tokens"""
        try:
            print(f"\n⚙️ Current settings:")
            print(f"   Temperature: {self.temperature}")
            print(f"   Max tokens: {self.max_tokens}")
            
            temp_input = input(f"New temperature (0.0-2.0, current: {self.temperature}): ").strip()
            if temp_input:
                self.temperature = float(temp_input)
                print(f"✅ Temperature set to: {self.temperature}")
            
            tokens_input = input(f"New max tokens (1-4096, current: {self.max_tokens}): ").strip()
            if tokens_input:
                self.max_tokens = int(tokens_input)
                print(f"✅ Max tokens set to: {self.max_tokens}")
        
        except ValueError:
            print("❌ Invalid input. Settings unchanged.")

def print_usage():
    """Print command line usage information"""
    print("🚀 vLLM Chat App")
    print("\nUsage:")
    print("  python3 chat_app_vllm.py                              # Interactive chat mode")
    print("  python3 chat_app_vllm.py \"your question\"              # Direct answer mode")
    print("  python3 chat_app_vllm.py [flags] \"your question\"      # Direct mode with options")
    print("  python3 chat_app_vllm.py -h, --help                  # Show this help")
    print("  python3 chat_app_vllm.py -v, --version               # Show version")
    print("\nFlags (for direct mode):")
    print("  --reasoning              # Enable step-by-step reasoning")
    print("  --no-stream             # Disable streaming (show complete response)")
    print("  --model MODEL_NAME      # Use specific model")
    print("  --url BASE_URL          # Use different vLLM server URL")
    print("\nExamples:")
    print("  python3 chat_app_vllm.py \"What is Python?\"")
    print("  python3 chat_app_vllm.py --reasoning \"Explain quantum computing\"")
    print("  python3 chat_app_vllm.py --url http://192.168.1.100:8000 \"Hello\"")
    print("  python3 chat_app_vllm.py --no-stream \"สวัสดี โลก!\"")
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
    print("  /settings  - Adjust temperature and max_tokens")
    print("  /status    - Show current settings")
    print("  /test      - Test connection to vLLM server")
    print("  /quit      - Exit the chat")
    print()

def handle_direct_prompt(prompt: str, base_url: str = "http://localhost:8000", model: str = "Qwen/Qwen3-4B-Instruct-2507"):
    """Handle direct prompt from command line arguments"""
    # Parse special flags from the prompt
    args = sys.argv[1:]
    reasoning_mode = False
    no_stream = False
    model_override = None
    url_override = None
    
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
        elif arg == '--url' and i + 1 < len(args):
            url_override = args[i + 1]
            i += 1  # Skip the next argument (URL)
        else:
            filtered_args.append(arg)
        i += 1
    
    # Rebuild prompt from filtered arguments
    if not filtered_args:
        print("❌ Error: No prompt provided after flags")
        return 1
    
    prompt = " ".join(filtered_args)
    
    print(f"🚀 vLLM Chat App - Direct Mode")
    print(f"📝 Prompt: {prompt}")
    if reasoning_mode:
        print("🧠 Reasoning mode: ON")
    if no_stream:
        print("📡 Streaming: OFF")
    if model_override:
        print(f"🔄 Model override: {model_override}")
    if url_override:
        print(f"🌐 URL override: {url_override}")
    print("-" * 50)
    
    # Initialize chat with overrides
    chat = VLLMChat(
        base_url=url_override if url_override else base_url,
        model=model_override if model_override else model
    )
    
    # Apply mode settings
    if reasoning_mode:
        chat.show_reasoning = True
        chat.reasoning_mode = "simple"  # Use simple mode for CLI
    if no_stream:
        chat.stream_response = False
    
    # Test connection
    print("🔗 Testing connection...")
    conn_status = chat.test_connection()
    print(conn_status)
    if "❌" in conn_status:
        return 1
    
    print()
    
    try:
        # Send the prompt and get response
        if chat.stream_response:
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
    """Main function"""
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Handle special flags
        if sys.argv[1] in ['-h', '--help']:
            print_usage()
            return 0
        elif sys.argv[1] in ['-v', '--version']:
            print("vLLM Chat App v1.0")
            return 0
        else:
            # Direct prompt mode - answer the question and exit
            return handle_direct_prompt("")
    
    print("🚀 vLLM Chat App - Interactive Mode")
    print("💡 Tip: You can also use direct mode: python3 chat_app_vllm.py \"your question\"")
    print("Type '/help' for commands or start chatting!")
    print("-" * 50)
    
    # Initialize chat
    chat = VLLMChat()
    
    # Test connection
    print("🔗 Testing connection to vLLM server...")
    conn_status = chat.test_connection()
    print(conn_status)
    
    if "❌" in conn_status:
        print("\n💡 Make sure your vLLM server is running:")
        print("llm-env/bin/python -m vllm.entrypoints.openai.api_server \\")
        print("  --model Qwen/Qwen3-4B-Instruct-2507 \\")
        print("  --host 0.0.0.0 --port 8000")
        return 1
    
    print(f"\n🤖 Using model: {chat.model}")
    reasoning_status = f"ON ({chat.reasoning_mode})" if chat.show_reasoning else "OFF"
    print(f"🧠 Reasoning mode: {reasoning_status}")
    streaming_status = "ON" if chat.stream_response else "OFF"
    print(f"📡 Streaming mode: {streaming_status}")
    print("💡 Tip: Use /reasoning for step-by-step thinking, /stream for real-time responses!")
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
                    filename = input("Enter filename (default: vllm_chat_history.json): ").strip()
                    if not filename:
                        filename = "vllm_chat_history.json"
                    chat.save_conversation(filename)
                elif command.startswith('/load'):
                    filename = input("Enter filename to load: ").strip()
                    if filename:
                        chat.load_conversation(filename)
                elif command.startswith('/model'):
                    new_model = input(f"Enter model name (current: {chat.model}): ").strip()
                    if new_model:
                        chat.change_model(new_model)
                elif command == '/reasoning':
                    chat.toggle_reasoning()
                elif command == '/rmode':
                    chat.change_reasoning_mode()
                elif command == '/stream':
                    chat.toggle_streaming()
                elif command == '/settings':
                    chat.adjust_settings()
                elif command == '/test':
                    conn_status = chat.test_connection()
                    print(conn_status)
                elif command == '/status':
                    print(f"\n📊 Current Settings:")
                    print(f"   🤖 Model: {chat.model}")
                    print(f"   🌐 Base URL: {chat.base_url}")
                    reasoning_status = f"ON ({chat.reasoning_mode})" if chat.show_reasoning else "OFF"
                    print(f"   🧠 Reasoning mode: {reasoning_status}")
                    streaming_status = "ON" if chat.stream_response else "OFF"
                    print(f"   📡 Streaming mode: {streaming_status}")
                    print(f"   🌡️  Temperature: {chat.temperature}")
                    print(f"   📏 Max tokens: {chat.max_tokens}")
                    print(f"   💬 Messages in history: {len(chat.conversation_history)}")
                else:
                    print("❓ Unknown command. Type '/help' for available commands.")
                continue
            
            # Send message to vLLM
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
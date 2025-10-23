#!/usr/bin/env python3
"""
OpenAI Chat App
A chat application for interacting with OpenAI's API (GPT-4, GPT-4o, GPT-3.5, etc.)
Supports the latest OpenAI models including GPT-4o and future models
"""
import openai
import os
import json
import sys
from typing import List, Dict

class OpenAIChat:
    def __init__(self, model: str = "gpt-4o", api_key: str = None):
        """Initialize OpenAI chat client
        
        Args:
            model: OpenAI model name (gpt-4o, gpt-4, gpt-3.5-turbo, etc.)
            api_key: OpenAI API key (or set OPENAI_API_KEY environment variable)
        """
        # Set up API key
        if api_key:
            openai.api_key = api_key
        elif os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
        else:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = openai.OpenAI(api_key=openai.api_key)
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        self.show_reasoning = False
        self.reasoning_mode = "simple"
        self.stream_response = True
        self.max_tokens = 2048
        self.temperature = 0.7
        
        # Reasoning prompts for different modes
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

🤔 **Quick Analysis**: What's being asked?
⚡ **Key Steps**: 
1. [Step 1]
2. [Step 2] 
3. [Step 3]
💡 **Answer**: [Your response]

Question: """,
            "chain": """
Let me think through this step by step:

Chain of thought:
- First, I need to understand...
- Then, I should consider...
- This leads me to think...
- Therefore, my conclusion is...

Question: """
        }

    def test_connection(self) -> str:
        """Test connection to OpenAI API"""
        try:
            # Test with a simple request
            response = self.client.models.list()
            available_models = [model.id for model in response.data]
            
            if self.model in available_models:
                model_status = f"✅ Model '{self.model}' is available"
            else:
                model_status = f"⚠️  Model '{self.model}' may not be available"
                # Suggest alternatives
                gpt_models = [m for m in available_models if 'gpt' in m.lower()]
                if gpt_models:
                    model_status += f"\\n💡 Available GPT models: {', '.join(gpt_models[:5])}"
            
            return f"✅ Connected to OpenAI API\\n{model_status}"
        except Exception as e:
            return f"❌ Failed to connect to OpenAI API: {str(e)}"

    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            response = self.client.models.list()
            models = [model.id for model in response.data]
            # Filter to commonly used models and sort
            preferred_models = ['gpt-4o', 'gpt-4o-mini', 'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
            available_preferred = [m for m in preferred_models if m in models]
            other_models = [m for m in models if m not in preferred_models and 'gpt' in m]
            return available_preferred + sorted(other_models)
        except Exception as e:
            print(f"Error getting models: {e}")
            return ['gpt-4o', 'gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo']  # Fallback

    def send_message(self, message: str) -> str:
        """Send message to OpenAI and get response"""
        try:
            # Add reasoning prompt if enabled
            if self.show_reasoning and message.strip():
                reasoning_prompt = self.reasoning_prompts.get(self.reasoning_mode, self.reasoning_prompts["simple"])
                message = reasoning_prompt + message

            # Prepare messages
            messages = self.conversation_history.copy()
            messages.append({"role": "user", "content": message})

            if self.stream_response:
                return self._send_streaming_message(messages)
            else:
                return self._send_regular_message(messages)

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _send_streaming_message(self, messages: List[Dict[str, str]]) -> str:
        """Send message with streaming response"""
        try:
            print("🤖 Bot: ", end="", flush=True)
            
            # Prepare parameters for API call
            params = {
                "model": self.model,
                "messages": messages,
                "stream": True
            }
            
            # GPT-5 models have strict parameter requirements
            if self.model.startswith('gpt-5'):
                # Only use default temperature for GPT-5 models
                params["max_completion_tokens"] = self.max_tokens
            else:
                # Other models support custom temperature
                params["temperature"] = self.temperature
                # Use correct parameter name based on model
                if self.model.startswith(('gpt-4o', 'chatgpt-4o')):
                    params["max_completion_tokens"] = self.max_tokens
                else:
                    params["max_tokens"] = self.max_tokens
            
            response = self.client.chat.completions.create(**params)
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print()  # New line after response
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": messages[-1]["content"]})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
            return full_response

        except Exception as e:
            print(f"\\n❌ Streaming error: {e}")
            return f"❌ Error: {str(e)}"

    def _send_regular_message(self, messages: List[Dict[str, str]]) -> str:
        """Send message with regular (non-streaming) response"""
        try:
            # Prepare parameters for API call
            params = {
                "model": self.model,
                "messages": messages
            }
            
            # GPT-5 models have strict parameter requirements
            if self.model.startswith('gpt-5'):
                # Only use default temperature for GPT-5 models
                params["max_completion_tokens"] = self.max_tokens
            else:
                # Other models support custom temperature
                params["temperature"] = self.temperature
                # Use correct parameter name based on model
                if self.model.startswith(('gpt-4o', 'chatgpt-4o')):
                    params["max_completion_tokens"] = self.max_tokens
                else:
                    params["max_tokens"] = self.max_tokens
            
            response = self.client.chat.completions.create(**params)
            
            response_text = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": messages[-1]["content"]})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️  Conversation history cleared.")

    def save_conversation(self, filename: str):
        """Save conversation to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'model': self.model,
                    'conversation': self.conversation_history,
                    'settings': {
                        'reasoning': self.show_reasoning,
                        'reasoning_mode': self.reasoning_mode,
                        'stream': self.stream_response,
                        'max_tokens': self.max_tokens,
                        'temperature': self.temperature
                    }
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Conversation saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")

    def load_conversation(self, filename: str):
        """Load conversation from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.conversation_history = data.get('conversation', [])
            if 'settings' in data:
                settings = data['settings']
                self.show_reasoning = settings.get('reasoning', False)
                self.reasoning_mode = settings.get('reasoning_mode', 'simple')
                self.stream_response = settings.get('stream', True)
                self.max_tokens = settings.get('max_tokens', 2048)
                self.temperature = settings.get('temperature', 0.7)
            
            print(f"📂 Conversation loaded from {filename}")
            print(f"📝 Messages: {len(self.conversation_history)}")
        except Exception as e:
            print(f"❌ Error loading conversation: {e}")

    def show_conversation_stats(self):
        """Show conversation statistics"""
        if not self.conversation_history:
            print("📊 No conversation history")
            return
        
        user_messages = len([msg for msg in self.conversation_history if msg["role"] == "user"])
        assistant_messages = len([msg for msg in self.conversation_history if msg["role"] == "assistant"])
        
        print(f"📊 Conversation Stats:")
        print(f"   👤 User messages: {user_messages}")
        print(f"   🤖 Assistant messages: {assistant_messages}")
        print(f"   💬 Total exchanges: {min(user_messages, assistant_messages)}")

def print_help():
    """Print help information"""
    print("""
🔧 Available Commands:
  /help         - Show this help message
  /clear        - Clear conversation history
  /save <file>  - Save conversation to file
  /load <file>  - Load conversation from file
  /model <name> - Switch to different OpenAI model
  /models       - List available models
  /reasoning    - Toggle step-by-step reasoning mode
  /rmode <type> - Set reasoning mode (simple, detailed, chain)
  /stream       - Toggle streaming responses
  /temp <val>   - Set temperature (0.0-2.0)
  /tokens <num> - Set max tokens limit
  /stats        - Show conversation statistics
  /status       - Show current settings
  /quit         - Exit the chat

💡 Tips:
  - Use reasoning mode for complex problems
  - Try different models for different tasks
  - Save conversations for later reference
  - Use temperature to control creativity (higher = more creative)
""")

def print_status(chat: OpenAIChat):
    """Print current status and settings"""
    print(f"📊 Current Settings:")
    print(f"   🤖 Model: {chat.model}")
    print(f"   🧠 Reasoning: {'ON (' + chat.reasoning_mode + ')' if chat.show_reasoning else 'OFF'}")
    print(f"   📡 Streaming: {'ON' if chat.stream_response else 'OFF'}")
    print(f"   🌡️  Temperature: {chat.temperature}")
    print(f"   📏 Max tokens: {chat.max_tokens}")
    print(f"   💬 Messages in history: {len(chat.conversation_history)}")

def handle_direct_prompt(prompt: str, model: str = "gpt-4o", api_key: str = None, 
                        no_stream: bool = False, reasoning: bool = False, 
                        temperature: float = 0.7, max_tokens: int = 2048):
    """Handle direct prompt from command line arguments"""
    try:
        chat = OpenAIChat(model=model, api_key=api_key)
        
        # Apply settings
        chat.stream_response = not no_stream
        chat.show_reasoning = reasoning
        chat.temperature = temperature
        chat.max_tokens = max_tokens
        
        # Test connection
        conn_status = chat.test_connection()
        if "❌" in conn_status:
            print(conn_status)
            return 1
        
        # Process the prompt
        response = chat.send_message(prompt)
        if not chat.stream_response:
            print(f"🤖 Bot: {response}")
        
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def main():
    """Main chat loop"""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenAI Chat Application")
    parser.add_argument("prompt", nargs="?", help="Direct prompt (non-interactive mode)")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model to use")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--reasoning", action="store_true", help="Enable reasoning mode")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature setting")
    parser.add_argument("--max-tokens", type=int, default=2048, help="Maximum tokens")
    
    args = parser.parse_args()
    
    # Handle direct prompt mode
    if args.prompt:
        return handle_direct_prompt(args.prompt, args.model, args.api_key, 
                                  args.no_stream, args.reasoning, 
                                  args.temperature, args.max_tokens)
    
    # Interactive mode
    print("🤖 OpenAI Chat App - Interactive Mode")
    print("💡 Tip: You can also use direct mode: python3 openai_chat.py \"your question\"")
    print("Type '/help' for commands or start chatting!")
    print("-" * 50)
    
    try:
        # Initialize chat
        chat = OpenAIChat(model=args.model, api_key=args.api_key)
        
        # Apply command line settings
        chat.show_reasoning = args.reasoning
        chat.stream_response = not args.no_stream
        chat.temperature = args.temperature
        chat.max_tokens = args.max_tokens
        
        # Test connection
        print("🔗 Testing connection to OpenAI...")
        conn_status = chat.test_connection()
        print(conn_status)
        
        if "❌" in conn_status:
            print("\\n💡 Make sure you have set your OpenAI API key:")
            print("export OPENAI_API_KEY='your-api-key-here'")
            return 1
        
        print(f"\\n🤖 Using model: {chat.model}")
        reasoning_status = f"ON ({chat.reasoning_mode})" if chat.show_reasoning else "OFF"
        stream_status = "ON" if chat.stream_response else "OFF"
        print(f"🧠 Reasoning mode: {reasoning_status}")
        print(f"📡 Streaming mode: {stream_status}")
        print("💡 Tip: Use /reasoning for step-by-step thinking, /stream for real-time responses!")
        print("Type your message and press Enter to chat!")
        print()

        # Chat loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    command_parts = user_input[1:].split()
                    command = command_parts[0].lower()
                    
                    if command == "help":
                        print_help()
                    elif command == "quit" or command == "exit":
                        print("👋 Goodbye!")
                        break
                    elif command == "clear":
                        chat.clear_conversation()
                    elif command == "save":
                        if len(command_parts) > 1:
                            filename = command_parts[1]
                            if not filename.endswith('.json'):
                                filename += '.json'
                            chat.save_conversation(filename)
                        else:
                            print("❌ Please specify filename: /save <filename>")
                    elif command == "load":
                        if len(command_parts) > 1:
                            filename = command_parts[1]
                            if not filename.endswith('.json'):
                                filename += '.json'
                            chat.load_conversation(filename)
                        else:
                            print("❌ Please specify filename: /load <filename>")
                    elif command == "model":
                        if len(command_parts) > 1:
                            new_model = command_parts[1]
                            chat.model = new_model
                            print(f"🤖 Switched to model: {new_model}")
                            # Test new model
                            conn_status = chat.test_connection()
                            print(conn_status)
                        else:
                            print("❌ Please specify model: /model <model_name>")
                    elif command == "models":
                        print("🤖 Getting available models...")
                        models = chat.get_available_models()
                        print("📋 Available OpenAI models:")
                        for i, model in enumerate(models, 1):
                            marker = "⭐" if model == chat.model else "  "
                            print(f"{marker} {i}. {model}")
                    elif command == "reasoning":
                        chat.show_reasoning = not chat.show_reasoning
                        status = f"ON ({chat.reasoning_mode})" if chat.show_reasoning else "OFF"
                        print(f"🧠 Reasoning mode: {status}")
                    elif command == "rmode":
                        if len(command_parts) > 1:
                            mode = command_parts[1].lower()
                            if mode in chat.reasoning_prompts:
                                chat.reasoning_mode = mode
                                print(f"🧠 Reasoning mode set to: {mode}")
                            else:
                                print("❌ Invalid reasoning mode. Available: simple, detailed, chain")
                        else:
                            print("❌ Please specify mode: /rmode <simple|detailed|chain>")
                    elif command == "stream":
                        chat.stream_response = not chat.stream_response
                        status = "ON" if chat.stream_response else "OFF"
                        print(f"📡 Streaming mode: {status}")
                    elif command == "temp":
                        if len(command_parts) > 1:
                            try:
                                temp = float(command_parts[1])
                                if 0.0 <= temp <= 2.0:
                                    chat.temperature = temp
                                    print(f"🌡️  Temperature set to: {temp}")
                                else:
                                    print("❌ Temperature must be between 0.0 and 2.0")
                            except ValueError:
                                print("❌ Invalid temperature value")
                        else:
                            print("❌ Please specify temperature: /temp <0.0-2.0>")
                    elif command == "tokens":
                        if len(command_parts) > 1:
                            try:
                                tokens = int(command_parts[1])
                                if tokens > 0:
                                    chat.max_tokens = tokens
                                    print(f"📏 Max tokens set to: {tokens}")
                                else:
                                    print("❌ Max tokens must be positive")
                            except ValueError:
                                print("❌ Invalid token count")
                        else:
                            print("❌ Please specify token count: /tokens <number>")
                    elif command == "stats":
                        chat.show_conversation_stats()
                    elif command == "status":
                        print_status(chat)
                    else:
                        print(f"❌ Unknown command: /{command}")
                        print("💡 Type /help for available commands")
                    
                    continue
                
                # Send message to OpenAI
                response = chat.send_message(user_input)
                if not chat.stream_response:
                    print(f"🤖 Bot: {response}")
                    
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except EOFError:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue

    except Exception as e:
        print(f"❌ Failed to initialize OpenAI chat: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
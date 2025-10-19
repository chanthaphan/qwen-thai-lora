#!/usr/bin/env python3
"""
Gradio GUI for LLM Chat App
A web-based interface for chatting with Ollama and vLLM models
"""
import gradio as gr
import requests
import os
import json
import sys
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class LLMGUIChat:
    def __init__(self):
        # Backend configuration
        self.backend = "ollama"  # Default to ollama
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'localhost:11434')
        self.vllm_host = os.environ.get('VLLM_HOST', 'localhost:8000')
        
        # API URLs
        self.ollama_api_url = f"http://{self.ollama_host}/api/generate"
        self.ollama_tags_url = f"http://{self.ollama_host}/api/tags"
        self.vllm_chat_url = f"http://{self.vllm_host}/v1/chat/completions"
        self.vllm_models_url = f"http://{self.vllm_host}/v1/models"
        
        # Model and conversation state
        self.available_models = {"ollama": [], "vllm": []}
        self.current_model = "llama3.1:8b"
        self.conversation_history = []
        self.show_reasoning = False
        self.reasoning_mode = "simple"
        self.stream_response = True
        
        # Load available models from both backends
        self._load_available_models()
        
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
    
    def _load_available_models(self):
        """Load available models from both Ollama and vLLM"""
        # Load Ollama models
        self.available_models["ollama"] = []
        try:
            response = requests.get(self.ollama_tags_url, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models["ollama"] = [model['name'] for model in models_data.get('models', [])]
        except requests.exceptions.RequestException:
            pass
        
        if not self.available_models["ollama"]:
            self.available_models["ollama"] = ["llama3.1:8b"]  # Default fallback
        
        # Load vLLM models
        self.available_models["vllm"] = []
        try:
            response = requests.get(self.vllm_models_url, timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models["vllm"] = [model['id'] for model in models_data.get('data', [])]
        except requests.exceptions.RequestException:
            pass
        
        if not self.available_models["vllm"]:
            self.available_models["vllm"] = ["Qwen/Qwen3-4B-Instruct-2507"]  # Default fallback
    
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
    
    def send_message_stream(self, message: str, history: List[Dict], backend: str, model: str, 
                          reasoning: bool, reasoning_mode: str):
        """Send message with streaming response"""
        if not message.strip():
            yield "", history, "❌ Please enter a message"
            return
        
        # Update settings
        self.backend = backend
        self.current_model = model
        self.show_reasoning = reasoning
        self.reasoning_mode = reasoning_mode
        
        # Add user message to conversation history and display
        self.conversation_history.append({"role": "user", "content": message})
        history.append({"role": "user", "content": message})
        
        # Initialize assistant message
        history.append({"role": "assistant", "content": ""})
        
        try:
            if self.backend == "ollama":
                yield from self._stream_ollama(message, history)
            else:  # vllm
                yield from self._stream_vllm(message, history)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {e}"
            history[-1]["content"] = f"❌ {error_msg}"
            yield "", history, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            history[-1]["content"] = f"❌ {error_msg}"
            yield "", history, error_msg
    
    def _stream_ollama(self, message: str, history: List[Dict]):
        """Stream response from Ollama backend"""
        # Build prompt
        if self.show_reasoning:
            reasoning_prompt = self.reasoning_prompts.get(self.reasoning_mode, self.reasoning_prompts["simple"])
            prompt = reasoning_prompt + message
        else:
            prompt = self._build_context()
        
        # Send request to Ollama
        response = requests.post(
            self.ollama_api_url,
            json={
                "model": self.current_model,
                "prompt": prompt,
                "stream": True
            },
            stream=True,
            timeout=600
        )
        
        if response.status_code != 200:
            error_msg = f"Error: HTTP {response.status_code} - {response.text}"
            history[-1]["content"] = f"❌ {error_msg}"
            yield "", history, error_msg
            return
        
        # Process streaming response
        ai_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'response' in chunk:
                        token = chunk['response']
                        ai_response += token
                        # Update the last message in history (assistant's response)
                        history[-1]["content"] = ai_response
                        yield "", history, f"🔄 Streaming from Ollama: {self.current_model}"
                    
                    if chunk.get('done', False):
                        break
                except json.JSONDecodeError:
                    continue
        
        # Add final response to conversation history
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        yield "", history, f"✅ Response completed using Ollama: {self.current_model}"
    
    def _stream_vllm(self, message: str, history: List[Dict]):
        """Stream response from vLLM backend"""
        # Prepare messages for vLLM (OpenAI-compatible format)
        messages = []
        
        # Add conversation history
        for msg in self.conversation_history[:-1]:  # Exclude the current message we just added
            messages.append(msg)
        
        # Add reasoning prompt if enabled
        if self.show_reasoning:
            reasoning_prompt = self.reasoning_prompts.get(self.reasoning_mode, self.reasoning_prompts["simple"])
            user_message = reasoning_prompt + message
        else:
            user_message = message
        
        messages.append({"role": "user", "content": user_message})
        
        # Send request to vLLM
        response = requests.post(
            self.vllm_chat_url,
            json={
                "model": self.current_model,
                "messages": messages,
                "stream": True,
                "max_tokens": 2048,
                "temperature": 0.7
            },
            stream=True,
            timeout=600
        )
        
        if response.status_code != 200:
            error_msg = f"Error: HTTP {response.status_code} - {response.text}"
            history[-1]["content"] = f"❌ {error_msg}"
            yield "", history, error_msg
            return
        
        # Process streaming response
        ai_response = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    line_str = line_str[6:]  # Remove 'data: ' prefix
                    if line_str.strip() == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(line_str)
                        if 'choices' in chunk and chunk['choices']:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                ai_response += delta['content']
                                # Update the last message in history (assistant's response)
                                history[-1]["content"] = ai_response
                                yield "", history, f"🔄 Streaming from vLLM: {self.current_model}"
                    except json.JSONDecodeError:
                        continue
        
        # Add final response to conversation history
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        yield "", history, f"✅ Response completed using vLLM: {self.current_model}"
    
    def send_message_non_stream(self, message: str, history: List[Dict], backend: str, model: str, 
                               reasoning: bool, reasoning_mode: str) -> Tuple[str, List[Dict], str]:
        """Send message without streaming (collect full response first)"""
        if not message.strip():
            return "", history, "❌ Please enter a message"
        
        # Update settings
        self.backend = backend
        self.current_model = model
        self.show_reasoning = reasoning
        self.reasoning_mode = reasoning_mode
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            if self.backend == "ollama":
                ai_response = self._get_ollama_response(message)
            else:  # vllm
                ai_response = self._get_vllm_response(message)
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Update chat history for display
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": ai_response})
            
            return "", history, f"✅ Response generated using {self.backend}: {self.current_model}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {e}"
            return "", history, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            return "", history, error_msg
    
    def _get_ollama_response(self, message: str) -> str:
        """Get complete response from Ollama (non-streaming)"""
        # Build prompt
        if self.show_reasoning:
            reasoning_prompt = self.reasoning_prompts.get(self.reasoning_mode, self.reasoning_prompts["simple"])
            prompt = reasoning_prompt + message
        else:
            prompt = self._build_context()
        
        # Send request to Ollama
        response = requests.post(
            self.ollama_api_url,
            json={
                "model": self.current_model,
                "prompt": prompt,
                "stream": False  # Non-streaming
            },
            timeout=600
        )
        
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"HTTP {response.status_code} - {response.text}")
        
        return response.json().get("response", "")
    
    def _get_vllm_response(self, message: str) -> str:
        """Get complete response from vLLM (non-streaming)"""
        # Prepare messages for vLLM
        messages = []
        for msg in self.conversation_history[:-1]:  # Exclude the current message we just added
            messages.append(msg)
        
        # Add reasoning prompt if enabled
        if self.show_reasoning:
            reasoning_prompt = self.reasoning_prompts.get(self.reasoning_mode, self.reasoning_prompts["simple"])
            user_message = reasoning_prompt + message
        else:
            user_message = message
        
        messages.append({"role": "user", "content": user_message})
        
        # Send request to vLLM
        response = requests.post(
            self.vllm_chat_url,
            json={
                "model": self.current_model,
                "messages": messages,
                "stream": False,  # Non-streaming
                "max_tokens": 2048,
                "temperature": 0.7
            },
            timeout=600
        )
        
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"HTTP {response.status_code} - {response.text}")
        
        response_data = response.json()
        if 'choices' in response_data and response_data['choices']:
            return response_data['choices'][0]['message']['content']
        return ""
    
    def clear_conversation(self) -> Tuple[List[Dict], str]:
        """Clear conversation history"""
        self.conversation_history = []
        return [], "🗑️ Conversation cleared"
    
    def save_conversation(self, filename: str) -> str:
        """Save conversation to file"""
        if not filename.strip():
            return "❌ Please provide a filename"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        try:
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "model": self.current_model,
                "conversation": self.conversation_history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            return f"💾 Conversation saved to {filename}"
        except Exception as e:
            return f"❌ Error saving conversation: {e}"
    
    def load_conversation(self, file) -> Tuple[List[Dict], str]:
        """Load conversation from file"""
        if file is None:
            return [], "❌ No file selected"
        
        try:
            with open(file.name, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            
            if 'conversation' in conversation_data:
                self.conversation_history = conversation_data['conversation']
                
                # Convert to display format (new Gradio messages format)
                history = []
                for msg in self.conversation_history:
                    history.append(msg)
                
                model_info = conversation_data.get('model', 'Unknown')
                timestamp = conversation_data.get('timestamp', 'Unknown')
                
                return history, f"📂 Conversation loaded (Model: {model_info}, Time: {timestamp})"
            else:
                return [], "❌ Invalid conversation file format"
                
        except Exception as e:
            return [], f"❌ Error loading conversation: {e}"
    
    def test_connection(self, backend: str = None) -> str:
        """Test connection to selected backend"""
        if backend is None:
            backend = self.backend
            
        if backend == "ollama":
            return self._test_ollama_connection()
        else:  # vllm
            return self._test_vllm_connection()
    
    def _test_ollama_connection(self) -> str:
        """Test connection to Ollama"""
        try:
            response = requests.get(self.ollama_tags_url, timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_count = len(models)
                return f"✅ Connected to Ollama at {self.ollama_host}\n📋 {model_count} models available"
            else:
                return f"⚠️ Ollama responded with status {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"❌ Cannot connect to Ollama: {e}\nMake sure Ollama is running with 'ollama serve'"
    
    def _test_vllm_connection(self) -> str:
        """Test connection to vLLM"""
        try:
            response = requests.get(self.vllm_models_url, timeout=5)
            if response.status_code == 200:
                models = response.json().get('data', [])
                model_count = len(models)
                return f"✅ Connected to vLLM at {self.vllm_host}\n📋 {model_count} models available"
            else:
                return f"⚠️ vLLM responded with status {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"❌ Cannot connect to vLLM: {e}\nMake sure vLLM server is running"
    
    def get_available_models(self, backend: str) -> List[str]:
        """Get available models for the selected backend"""
        return self.available_models.get(backend, [])

def create_gui():
    """Create and configure the Gradio interface"""
    
    # Initialize chat instance
    try:
        chat = LLMGUIChat()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please check environment variables (OLLAMA_HOST, VLLM_HOST)")
        sys.exit(1)
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
    }
    .chat-container {
        height: 600px !important;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    """
    
    # Create Gradio interface
    with gr.Blocks(css=custom_css, title="LLM Chat GUI") as interface:
        gr.Markdown("# 🤖 LLM Chat GUI")
        gr.Markdown("Web interface for chatting with Ollama and vLLM models")
        
        with gr.Row():
            with gr.Column(scale=3):
                # Chat interface
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    height=500,
                    show_copy_button=True,
                    type="messages"
                )
                
                with gr.Row():
                    message_input = gr.Textbox(
                        placeholder="Type your message here...",
                        container=False,
                        scale=4,
                        autofocus=True
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Status display
                status_display = gr.Textbox(
                    label="Status",
                    value="Ready",
                    interactive=False,
                    max_lines=3
                )
            
            with gr.Column(scale=1):
                # Settings panel
                gr.Markdown("### ⚙️ Settings")
                
                # Backend selection
                backend_dropdown = gr.Dropdown(
                    choices=["ollama", "vllm"],
                    value="ollama",
                    label="Backend",
                    info="Select LLM backend"
                )
                
                # Model selection (will be updated based on backend)
                model_dropdown = gr.Dropdown(
                    choices=chat.available_models["ollama"],
                    value=chat.current_model,
                    label="Model",
                    info="Select model"
                )
                
                reasoning_checkbox = gr.Checkbox(
                    label="Enable Reasoning",
                    value=False,
                    info="Show step-by-step thinking"
                )
                
                reasoning_mode_dropdown = gr.Dropdown(
                    choices=["simple", "detailed", "chain"],
                    value="simple",
                    label="Reasoning Mode",
                    info="Type of reasoning to show"
                )
                
                streaming_checkbox = gr.Checkbox(
                    label="Enable Streaming",
                    value=True,
                    info="Stream responses in real-time"
                )
                
                # Connection test
                gr.Markdown("### 🔌 Connection")
                test_btn = gr.Button("Test Connection", variant="secondary")
                connection_status = gr.Textbox(
                    label="Connection Status",
                    interactive=False,
                    max_lines=3
                )
                
                # Conversation management
                gr.Markdown("### 💾 Conversation")
                
                with gr.Row():
                    clear_btn = gr.Button("Clear", variant="secondary")
                
                save_filename = gr.Textbox(
                    placeholder="conversation.json",
                    label="Save Filename",
                    info="Enter filename to save conversation"
                )
                save_btn = gr.Button("Save Conversation", variant="secondary")
                
                load_file = gr.File(
                    label="Load Conversation",
                    file_types=[".json"],
                    type="filepath"
                )
    
        # Event handlers
        def handle_send(message, history, backend, model, reasoning, reasoning_mode, streaming):
            """Handle message sending with streaming support"""
            if streaming:
                # Use streaming generator
                yield from chat.send_message_stream(message, history, backend, model, reasoning, reasoning_mode)
            else:
                # Use non-streaming but wrap in generator for consistency
                result = chat.send_message_non_stream(message, history, backend, model, reasoning, reasoning_mode)
                yield result
        
        def handle_clear():
            return chat.clear_conversation()
        
        def handle_save(filename):
            return chat.save_conversation(filename)
        
        def handle_load(file):
            return chat.load_conversation(file)
        
        def handle_test(backend):
            return chat.test_connection(backend)
        
        def handle_backend_change(backend):
            """Update available models when backend changes"""
            models = chat.get_available_models(backend)
            default_model = models[0] if models else ""
            return gr.Dropdown(choices=models, value=default_model)
        
        # Connect events
        send_btn.click(
            fn=handle_send,
            inputs=[message_input, chatbot, backend_dropdown, model_dropdown, reasoning_checkbox, reasoning_mode_dropdown, streaming_checkbox],
            outputs=[message_input, chatbot, status_display]
        )
        
        message_input.submit(
            fn=handle_send,
            inputs=[message_input, chatbot, backend_dropdown, model_dropdown, reasoning_checkbox, reasoning_mode_dropdown, streaming_checkbox],
            outputs=[message_input, chatbot, status_display]
        )
        
        # Backend change event
        backend_dropdown.change(
            fn=handle_backend_change,
            inputs=[backend_dropdown],
            outputs=[model_dropdown]
        )
        
        clear_btn.click(
            fn=handle_clear,
            outputs=[chatbot, status_display]
        )
        
        save_btn.click(
            fn=handle_save,
            inputs=[save_filename],
            outputs=[status_display]
        )
        
        load_file.change(
            fn=handle_load,
            inputs=[load_file],
            outputs=[chatbot, status_display]
        )
        
        test_btn.click(
            fn=handle_test,
            inputs=[backend_dropdown],
            outputs=[connection_status]
        )
        
        # Initialize connection status on load
        interface.load(
            fn=lambda: chat.test_connection("ollama"),
            outputs=[connection_status]
        )
    
    return interface

def main():
    """Main function to launch the GUI"""
    print("🚀 Starting LLM Chat GUI...")
    
    # Check environment (optional - will use defaults if not set)
    ollama_host = os.environ.get('OLLAMA_HOST', 'localhost:11434')
    vllm_host = os.environ.get('VLLM_HOST', 'localhost:8000')
    print(f"📡 Ollama host: {ollama_host}")
    print(f"📡 vLLM host: {vllm_host}")
    
    try:
        # Create and launch interface
        interface = create_gui()
        
        print("🌐 Launching web interface...")
        print("💡 The interface will open in your default browser")
        print("🔧 Use Ctrl+C to stop the server")
        
        # Launch with custom settings
        interface.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7861,       # Use different port to avoid conflicts
            share=False,            # Set to True to create public link
            show_error=True,
            inbrowser=False         # Don't auto-open browser to avoid gio error
        )
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        return 0
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        sys.exit(exit_code)
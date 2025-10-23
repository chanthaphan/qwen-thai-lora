#!/usr/bin/env python3
"""
Enhanced Web Chat Interface with PostgreSQL Storage
Extends the existing web_chat.py with database-backed conversation persistence
"""
import gradio as gr
import os
import sys
import uuid
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from thai_model.interfaces.web_chat import LLMGUIChat
from thai_model.core.chat_database import ChatDatabaseManager

class DatabaseLLMGUIChat(LLMGUIChat):
    """Enhanced LLM Chat with PostgreSQL database integration"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize database
        self.database_enabled = False
        self.db_manager = None
        self.current_session_id = None
        self.session_name = None
        
        try:
            from thai_model.core.chat_database import ChatDatabaseManager
            self.db_manager = ChatDatabaseManager()
            self.database_enabled = True
            print("✅ Database connection established")
        except Exception as e:
            print(f"⚠️  Database not available: {e}")
            print("💡 Run './setup_postgres.sh' to set up PostgreSQL")
    

        
    def start_new_session(self, backend: str, model: str, session_name: str = None) -> str:
        """Start a new conversation session"""
        if self.database_enabled and self.db_manager:
            self.current_session_id = self.db_manager.create_session(backend, model, session_name)
            self.session_name = session_name or f"{backend}-{model}-{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        else:
            # Fallback to memory-only
            self.current_session_id = str(uuid.uuid4())
            self.session_name = session_name or f"memory-session-{datetime.now().strftime('%H:%M')}"
        
        # Clear in-memory history for new session
        self.conversation_history = []
        return self.current_session_id
    
    def add_message_to_db(self, role: str, content: str, metadata: Dict = None):
        """Add message to database if available"""
        if self.database_enabled and self.db_manager and self.current_session_id:
            try:
                self.db_manager.add_message(self.current_session_id, role, content, metadata or {})
            except Exception as e:
                print(f"⚠️ Failed to save message to database: {e}")
    
    def load_session_history(self, session_id: str) -> bool:
        """Load conversation history from database"""
        if not self.database_enabled or not self.db_manager:
            return False
        
        try:
            # Get session info
            session_info = self.db_manager.get_session_info(session_id)
            if not session_info:
                return False
            
            # Load conversation history
            messages = self.db_manager.get_conversation_history(session_id)
            
            # Convert to internal format
            self.conversation_history = []
            for msg in messages:
                self.conversation_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Set current session
            self.current_session_id = session_id
            self.session_name = session_info["session_name"]
            self.backend = session_info["backend"]
            self.current_model = session_info["model"]
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load session: {e}")
            return False
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent chat sessions"""
        if not self.database_enabled or not self.db_manager:
            return []
        
        try:
            return self.db_manager.list_sessions(limit)
        except Exception as e:
            print(f"❌ Failed to get recent sessions: {e}")
            return []
    
    def load_session_history(self, session_id: str) -> Tuple[List[Dict], str]:
        """Load conversation history from database in messages format"""
        if not self.database_enabled or not self.db_manager:
            return [], "❌ Database not available"
        
        try:
            # Get session info first
            session_info = self.db_manager.get_session_info(session_id)
            if not session_info:
                return [], "❌ Session not found"
            
            messages = self.db_manager.get_conversation_history(session_id)
            # Convert to internal dict format
            dict_history = []
            for msg in messages:
                dict_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Update internal conversation history and session info
            self.conversation_history = dict_history
            self.current_session_id = session_id
            self.session_name = session_info["session_name"]
            
            return dict_history, f"✅ Loaded conversation with {len(messages)} messages"
        except Exception as e:
            return [], f"❌ Failed to load session: {e}"
    
    def send_message_stream(self, message: str, history: List[Dict], backend: str, 
                          model: str, reasoning: bool, reasoning_mode: str):
        """Enhanced send message with database storage using messages format"""
        # Set current backend and model
        self.backend = backend
        self.current_model = model
        self.show_reasoning = reasoning
        self.reasoning_mode = reasoning_mode
        
        # Start new session if none exists
        if not self.current_session_id:
            self.start_new_session(backend, model)
        
        # Add user message to database
        self.add_message_to_db("user", message)
        
        # Call parent streaming method - now using messages format directly
        for empty_msg, messages, status in super().send_message_stream(message, history, backend, model, reasoning, reasoning_mode):
            yield empty_msg, messages, status
        
        # Add assistant response to database (get the last assistant message)
        if self.conversation_history and self.conversation_history[-1]["role"] == "assistant":
            assistant_message = self.conversation_history[-1]["content"]
            self.add_message_to_db("assistant", assistant_message, {
                "backend": backend,
                "model": model,
                "reasoning_enabled": reasoning,
                "reasoning_mode": reasoning_mode if reasoning else None
            })
    
    def send_message_non_stream(self, message: str, history: List[Dict], backend: str, 
                              model: str, reasoning: bool, reasoning_mode: str) -> Tuple[str, List[Dict], str]:
        """Enhanced non-streaming send with database storage using messages format"""
        # Set current backend and model
        self.backend = backend
        self.current_model = model
        self.show_reasoning = reasoning
        self.reasoning_mode = reasoning_mode
        
        # Start new session if none exists
        if not self.current_session_id:
            self.start_new_session(backend, model)
        
        # Add user message to database
        self.add_message_to_db("user", message)
        
        # Call parent non-streaming method - now using messages format directly
        empty_msg, messages, status = super().send_message_non_stream(message, history, backend, model, reasoning, reasoning_mode)
        
        # Add assistant response to database
        if self.conversation_history and self.conversation_history[-1]["role"] == "assistant":
            assistant_message = self.conversation_history[-1]["content"]
            self.add_message_to_db("assistant", assistant_message, {
                "backend": backend,
                "model": model,
                "reasoning_enabled": reasoning,
                "reasoning_mode": reasoning_mode if reasoning else None
            })
        
        return empty_msg, messages, status
    
    def clear_conversation(self) -> Tuple[List[Dict], str]:
        """Clear current conversation"""
        self.current_session_id = None
        self.session_name = None
        messages, status = super().clear_conversation()
        return messages, status
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        if not self.database_enabled or not self.db_manager:
            return {"error": "Database not available"}
        
        try:
            return self.db_manager.get_statistics()
        except Exception as e:
            return {"error": f"Failed to get stats: {e}"}

def create_enhanced_gui():
    """Create enhanced Gradio interface with database features"""
    
    # Initialize chat instance
    try:
        chat = DatabaseLLMGUIChat()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Custom CSS
    custom_css = """
    .database-info { 
        background: linear-gradient(45deg, #1e3c72, #2a5298); 
        color: white; 
        padding: 10px; 
        border-radius: 8px; 
        margin: 10px 0;
    }
    .session-info {
        background: #f0f0f0;
        padding: 8px;
        border-radius: 5px;
        margin: 5px 0;
    }
    """
    
    # Create interface
    with gr.Blocks(css=custom_css, title="🇹🇭 Thai Model Chat (Database Edition)") as interface:
        
        gr.Markdown("""
        # 🇹🇭 Thai Model Chat Interface (Database Edition)
        ### Multi-backend LLM chat with PostgreSQL persistence
        **Supports:** Thai Model (vLLM) • Ollama • OpenAI (GPT-4, GPT-5) • **Persistent Chat History**
        """)
        
        # Database status
        if chat.database_enabled:
            gr.Markdown("""
            <div class="database-info">
                🐘 <strong>Database Status:</strong> Connected to PostgreSQL<br>
                💾 <strong>Persistence:</strong> All conversations are automatically saved<br>
                🔍 <strong>Features:</strong> Session management, search, statistics
            </div>
            """)
        else:
            gr.Markdown("""
            <div style="background: #ffeb3b; color: #333; padding: 10px; border-radius: 8px; margin: 10px 0;">
                ⚠️ <strong>Database Status:</strong> Not available - using memory-only storage<br>
                💡 <strong>Setup:</strong> Run <code>./setup_postgres.sh</code> to enable persistence
            </div>
            """)
        
        with gr.Row():
            with gr.Column(scale=3):
                # Chat interface
                chatbot = gr.Chatbot(
                    height=600,
                    show_copy_button=True,
                    label="💬 Conversation",
                    type="messages"
                )
                
                message_input = gr.Textbox(
                    placeholder="Type your message here...",
                    lines=3,
                    label="Your Message"
                )
                
                with gr.Row():
                    send_btn = gr.Button("🚀 Send", variant="primary")
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")
                
                # Backend and model selection
                backend_choices = ["ollama", "vllm"]
                if chat.openai_client:
                    backend_choices.append("openai")
                
                backend_dropdown = gr.Dropdown(
                    choices=backend_choices,
                    value="ollama",
                    label="Backend",
                    info="Select LLM backend"
                )
                
                model_dropdown = gr.Dropdown(
                    choices=chat.available_models["ollama"],
                    value=chat.current_model,
                    label="Model",
                    info="Select model"
                )
                
                # Chat settings
                reasoning_checkbox = gr.Checkbox(
                    label="Enable Reasoning",
                    value=False
                )
                
                reasoning_mode_dropdown = gr.Dropdown(
                    choices=["simple", "detailed", "chain"],
                    value="simple",
                    label="Reasoning Mode"
                )
                
                streaming_checkbox = gr.Checkbox(
                    label="Enable Streaming",
                    value=True
                )
                
                # Session management
                if chat.database_enabled:
                    gr.Markdown("### 📚 Session Management")
                    
                    new_session_btn = gr.Button("🆕 New Session", variant="secondary")
                    
                    recent_sessions_dropdown = gr.Dropdown(
                        label="Recent Sessions",
                        info="Load a previous conversation"
                    )
                    
                    load_session_btn = gr.Button("📥 Load Session")
                    
                    # Database stats
                    with gr.Accordion("📊 Database Statistics", open=False):
                        stats_btn = gr.Button("Refresh Stats")
                        stats_display = gr.JSON(label="Statistics")
                
                # Status display
                status_display = gr.Textbox(
                    label="Status",
                    interactive=False,
                    lines=2
                )
        
        # Event handlers
        def handle_send(message, history, backend, model, reasoning, reasoning_mode, streaming):
            """Handle message sending with database support"""
            if streaming:
                yield from chat.send_message_stream(message, history, backend, model, reasoning, reasoning_mode)
            else:
                result = chat.send_message_non_stream(message, history, backend, model, reasoning, reasoning_mode)
                yield result
        
        def handle_clear():
            return chat.clear_conversation()
        
        def handle_backend_change(backend):
            """Update models when backend changes"""
            models = chat.get_available_models(backend)
            default_model = models[0] if models else ""
            return gr.Dropdown(choices=models, value=default_model)
        
        def handle_new_session():
            """Start a new session"""
            session_id = chat.start_new_session("ollama", "llama3.1:8b")
            return [], f"🆕 Started new session: {session_id[:8]}..."
        
        def get_recent_sessions():
            """Get recent sessions for dropdown"""
            sessions = chat.get_recent_sessions()
            choices = []
            for session in sessions:
                label = f"{session['session_name']} ({session['message_count']} msgs)"
                choices.append((label, session['session_id']))
            return gr.Dropdown(choices=choices)
        
        def handle_load_session(session_id):
            """Load selected session"""
            if not session_id:
                return [], "❌ No session selected"
            
            history, status_msg = chat.load_session_history(session_id)
            if history:
                return history, f"✅ Loaded session: {chat.session_name}"
            else:
                return [], status_msg
        
        def get_database_stats():
            """Get database statistics"""
            return chat.get_database_stats()
        
        # Connect events
        send_btn.click(
            fn=handle_send,
            inputs=[message_input, chatbot, backend_dropdown, model_dropdown, 
                   reasoning_checkbox, reasoning_mode_dropdown, streaming_checkbox],
            outputs=[message_input, chatbot, status_display]
        )
        
        message_input.submit(
            fn=handle_send,
            inputs=[message_input, chatbot, backend_dropdown, model_dropdown, 
                   reasoning_checkbox, reasoning_mode_dropdown, streaming_checkbox],
            outputs=[message_input, chatbot, status_display]
        )
        
        clear_btn.click(
            fn=handle_clear,
            outputs=[chatbot, status_display]
        )
        
        backend_dropdown.change(
            fn=handle_backend_change,
            inputs=[backend_dropdown],
            outputs=[model_dropdown]
        )
        
        # Database-specific events
        if chat.database_enabled:
            new_session_btn.click(
                fn=handle_new_session,
                outputs=[chatbot, status_display]
            )
            
            interface.load(
                fn=get_recent_sessions,
                outputs=[recent_sessions_dropdown]
            )
            
            load_session_btn.click(
                fn=handle_load_session,
                inputs=[recent_sessions_dropdown],
                outputs=[chatbot, status_display]
            )
            
            stats_btn.click(
                fn=get_database_stats,
                outputs=[stats_display]
            )
    
    return interface

def main():
    """Main function to launch the enhanced chat interface"""
    print("🚀 Starting Enhanced LLM Chat GUI with PostgreSQL...")
    
    # Configuration
    ollama_host = os.environ.get('OLLAMA_HOST', 'localhost:11434')
    vllm_host = os.environ.get('VLLM_HOST', 'localhost:8000')
    
    print(f"📡 Ollama host: {ollama_host}")
    print(f"📡 vLLM host: {vllm_host}")
    
    # Create and launch interface
    interface = create_enhanced_gui()
    
    print("🌐 Launching enhanced web interface...")
    print("💡 The interface will open in your default browser")
    print("🔧 Use Ctrl+C to stop the server")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7862,  # Different port to avoid conflicts
        share=False,
        inbrowser=True
    )

if __name__ == "__main__":
    main()
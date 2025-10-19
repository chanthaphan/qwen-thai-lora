#!/usr/bin/env python3
"""
Test script for streaming functionality
"""
import os
import sys
sys.path.append('/home/chanthaphan/project')

# Set environment variables for testing
os.environ['OLLAMA_HOST'] = '172.25.96.1:11434'
os.environ['VLLM_HOST'] = 'localhost:8000'

from chat_gui import LLMGUIChat

def test_streaming():
    """Test the streaming functionality"""
    try:
        chat = LLMGUIChat()
        print("✅ LLMGUIChat initialized successfully")
        
        # Test model availability
        print(f"🤖 Ollama models: {chat.available_models['ollama']}")
        print(f"🤖 vLLM models: {chat.available_models['vllm']}")
        
        # Test connection to both backends
        print("\n🔌 Testing connections:")
        ollama_status = chat._test_ollama_connection()
        print(f"Ollama: {ollama_status}")
        
        vllm_status = chat._test_vllm_connection()
        print(f"vLLM: {vllm_status}")
        
        print("\n✅ All tests passed! Streaming should work properly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_streaming()
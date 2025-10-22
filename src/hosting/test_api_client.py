#!/usr/bin/env python3
"""
API Client Test Script
Comprehensive testing of the Thai Model FastAPI server
"""

import requests
import json
import time

class ThaiAPIClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_connection(self):
        """Test if the server is running"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
    
    def get_server_info(self):
        """Get server information"""
        response = self.session.get(f"{self.base_url}/")
        return response.json()
    
    def health_check(self):
        """Check server health"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def list_models(self):
        """List available models"""
        response = self.session.get(f"{self.base_url}/v1/models")
        return response.json()
    
    def summarize_text(self, text, max_tokens=150, temperature=0.7):
        """Summarize Thai text using the custom endpoint"""
        data = {
            "text": text,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = self.session.post(f"{self.base_url}/v1/summarize", json=data)
        return response.json()
    
    def chat_completion(self, messages, max_tokens=150, temperature=0.7):
        """Chat completion using OpenAI-compatible endpoint"""
        data = {
            "model": "thai-qwen-lora",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = self.session.post(f"{self.base_url}/v1/chat/completions", json=data)
        return response.json()

def main():
    """Test all API endpoints"""
    print("🧪 Thai Model API Client Test")
    print("=" * 50)
    
    client = ThaiAPIClient()
    
    # Test connection
    print("\n🔌 Testing connection...")
    if client.test_connection():
        print("✅ Connected to API server")
    else:
        print("❌ Cannot connect to API server")
        print("💡 Make sure the server is running: ./manage.sh host-api")
        return 1
    
    # Server info
    print("\n📋 Server Information:")
    info = client.get_server_info()
    print(f"   Message: {info['message']}")
    print(f"   Model: {info['model']}")
    
    # Health check
    print("\n🏥 Health Check:")
    health = client.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Model Loaded: {health['model_loaded']}")
    
    # List models
    print("\n🤖 Available Models:")
    models = client.list_models()
    for model in models['data']:
        print(f"   • {model['id']} (owned by: {model['owned_by']})")
    
    # Test summarization
    print("\n📝 Testing Text Summarization:")
    test_text = "นักวิทยาศาสตร์จากมหาวิทยาลัยชั้นนำได้พัฒนาเทคโนโลยีปัญญาประดิษฐ์ใหม่ที่สามารถช่วยในการวินิจฉัยโรคมะเร็งได้อย่างแม่นยำมากขึ้น โดยใช้การเรียนรู้เชิงลึกในการวิเคราะห์ภาพถ่ายทางการแพทย์ จากการทดสอบพบว่าระบบนี้สามารถตระหนักถึงความผิดปกติได้ถึง 95% ซึ่งสูงกว่าการวินิจฉัยแบบดั้งเดิมถึง 15% นอกจากนี้ระบบยังสามารถให้ผลการวินิจฉัยได้เร็วกว่าเดิมถึง 3 เท่า"
    
    print(f"   Input: {test_text[:100]}...")
    
    start_time = time.time()
    summary_result = client.summarize_text(test_text, max_tokens=100)
    summary_time = time.time() - start_time
    
    print(f"   Summary: {summary_result['summary']}")
    print(f"   Tokens: {summary_result['usage']['total_tokens']}")
    print(f"   Time: {summary_time:.2f}s")
    
    # Test chat completion
    print("\n💬 Testing Chat Completion:")
    messages = [
        {"role": "user", "content": "สรุปประโยชน์ของการออกกำลังกาย"}
    ]
    
    start_time = time.time()
    chat_result = client.chat_completion(messages, max_tokens=80)
    chat_time = time.time() - start_time
    
    print(f"   Question: {messages[0]['content']}")
    print(f"   Response: {chat_result['choices'][0]['message']['content']}")
    print(f"   Tokens: {chat_result['usage']['total_tokens']}")
    print(f"   Time: {chat_time:.2f}s")
    
    # Performance summary
    print(f"\n📊 Performance Summary:")
    print(f"   • Summarization: {summary_time:.2f}s")
    print(f"   • Chat completion: {chat_time:.2f}s")
    print(f"   • Model loaded on first request")
    
    print(f"\n🎉 All API tests completed successfully!")
    print(f"💡 You can now integrate with this API using:")
    print(f"   • Python requests library")
    print(f"   • OpenAI Python client (chat completions)")
    print(f"   • cURL commands")
    print(f"   • Any HTTP client")

if __name__ == "__main__":
    import sys
    try:
        exit_code = main()
        sys.exit(exit_code if exit_code else 0)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Thai Model Learning Launcher
===========================

Master script to guide you through the complete learning journey.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"🎓 {title}")
    print(f"{'='*70}\n")

def run_module(script_name):
    """Run a learning module script."""
    script_path = Path(__file__).parent / script_name
    if script_path.exists():
        subprocess.run([sys.executable, str(script_path)])
    else:
        print(f"❌ Module script not found: {script_name}")

def main():
    print_header("Thai Language Model - Complete Learning Journey")
    
    print("""
🌟 Welcome to your comprehensive Thai Model learning adventure!

This interactive learning system will guide you through mastering:
• Python package development
• Machine learning with transformers
• API development with FastAPI  
• Production deployment with Docker
• Advanced optimization and monitoring

📚 Available Learning Modules:
""")

    modules = {
        "1": {
            "title": "🐍 Module 1.1: Python Package Architecture",
            "script": "module_1_1_package_architecture.py",
            "description": "Master modern Python project structure and imports"
        },
        "2": {
            "title": "⚙️ Module 1.2: Configuration Management",
            "script": "module_1_2_configuration.py", 
            "description": "Learn YAML configs and dataclasses"
        },
        "3": {
            "title": "🧠 Module 2.1: Transformers & LoRA",
            "script": "module_2_1_transformers_lora.py",
            "description": "Understand transformer architecture and fine-tuning"
        },
        "4": {
            "title": "📈 Module 2.2: Model Training & Fine-tuning",
            "script": "module_2_2_training.py",
            "description": "Learn model training pipelines and LoRA techniques"
        },
        "5": {
            "title": "🚀 Module 3.1: FastAPI Fundamentals", 
            "script": "module_3_1_fastapi.py",
            "description": "Master modern API development with async/await"
        },
        "6": {
            "title": "⚡ Module 3.2: Advanced API Features",
            "script": "module_3_2_advanced_api.py", 
            "description": "Streaming, auth, rate limiting, and production features"
        },
        "7": {
            "title": "🐳 Module 4.1: Docker Mastery",
            "script": "module_4_1_docker.py",
            "description": "Containerization, multi-stage builds, and orchestration"
        },
        "8": {
            "title": "🏭 Module 4.2: Production Deployment",
            "script": "module_4_2_deployment.py",
            "description": "DevOps, monitoring, and scaling (Coming Soon)"
        },
        "p": {
            "title": "📊 Progress Tracker",
            "script": "progress_tracker.py",
            "description": "Track your learning progress and notes"
        },
        "r": {
            "title": "📖 Read Learning Path",
            "script": None,
            "description": "View the complete learning curriculum"
        }
    }
    
    # Display menu
    for key, module in modules.items():
        if module["script"]:
            available = "✅" if (Path(__file__).parent / module["script"]).exists() else "🔄"
        else:
            available = "✅"
        print(f"  {key}. {available} {module['title']}")
        print(f"      {module['description']}")
    
    print(f"\n  q. 🚪 Exit")
    
    while True:
        choice = input(f"\n🎯 Select module (1-8, p, r, q): ").strip().lower()
        
        if choice == 'q':
            print(f"\n👋 Happy learning! Your Thai Model journey awaits!")
            print(f"💡 Tip: Start with Module 1.1 if you're new to the codebase")
            break
            
        elif choice == 'r':
            # Show learning path
            learning_path = Path(__file__).parent.parent / "LEARNING_PATH.md"
            if learning_path.exists():
                print(f"\n📖 Opening LEARNING_PATH.md...")
                if os.name == 'nt':  # Windows
                    os.startfile(learning_path)
                else:  # Linux/Mac
                    subprocess.run(['less', str(learning_path)])
            else:
                print(f"❌ LEARNING_PATH.md not found")
                
        elif choice in modules:
            module = modules[choice]
            if module["script"]:
                print(f"\n🚀 Starting: {module['title']}")
                print(f"📝 {module['description']}")
                input(f"\nPress Enter to continue...")
                run_module(module["script"])
            else:
                print(f"❌ Module not implemented yet: {module['title']}")
                
        else:
            print(f"❌ Invalid choice. Please select 1-8, p, r, or q")

if __name__ == "__main__":
    main()
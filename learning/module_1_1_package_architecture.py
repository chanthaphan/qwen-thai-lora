#!/usr/bin/env python3
"""
Module 1.1: Python Package Architecture
=====================================

Interactive learning script to understand the Thai Model package structure.
"""

import os
import sys
import importlib
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎓 {title}")
    print(f"{'='*60}\n")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"📚 Step {step_num}: {description}")
    print("-" * 40)

def main():
    print_header("Module 1.1: Python Package Architecture")
    
    # Step 1: Explore package structure
    print_step(1, "Explore Package Structure")
    
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Show main package structure
    thai_model_path = project_root / "thai_model"
    if thai_model_path.exists():
        print(f"\n📦 thai_model/ package structure:")
        for item in thai_model_path.iterdir():
            if item.is_dir():
                print(f"  📁 {item.name}/")
                # Show submodules
                for subitem in item.iterdir():
                    if subitem.suffix == '.py':
                        print(f"    📄 {subitem.name}")
            elif item.suffix == '.py':
                print(f"  📄 {item.name}")
    
    input("\n🔍 Press Enter to continue to Step 2...")
    
    # Step 2: Understand pyproject.toml
    print_step(2, "Understanding pyproject.toml")
    
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        print(f"\n📋 Reading pyproject.toml:")
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        # Extract key sections
        sections = ['[build-system]', '[project]', '[project.dependencies]', '[tool.']
        for section in sections:
            if section in content:
                print(f"\n✅ Found section: {section}")
            else:
                print(f"\n❌ Missing section: {section}")
    
    input("\n🔍 Press Enter to continue to Step 3...")
    
    # Step 3: Test imports
    print_step(3, "Testing Package Imports")
    
    try:
        # Add project root to Python path
        sys.path.insert(0, str(project_root))
        
        # Test basic import
        print("🧪 Testing: import thai_model")
        import thai_model
        print(f"✅ Success! Version: {getattr(thai_model, '__version__', 'Unknown')}")
        
        # Test config import
        print("\n🧪 Testing: from thai_model.core.config import ModelConfig")
        from thai_model.core.config import ModelConfig
        print("✅ Success! ModelConfig imported")
        
        # Show available attributes
        print(f"\n📊 ModelConfig attributes:")
        for attr in dir(ModelConfig):
            if not attr.startswith('_'):
                print(f"  • {attr}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 This is normal if dependencies aren't installed")
    
    input("\n🔍 Press Enter to continue to Step 4...")
    
    # Step 4: Virtual Environment Check
    print_step(4, "Virtual Environment & Dependencies")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    print(f"🐍 Python executable: {sys.executable}")
    print(f"🏠 Virtual environment: {'Yes' if in_venv else 'No'}")
    
    if in_venv:
        print("✅ Good! You're using a virtual environment")
    else:
        print("⚠️  Consider using a virtual environment:")
        print("   python -m venv llm-env")
        print("   source llm-env/bin/activate")
    
    # Check for key dependencies
    key_deps = ['torch', 'transformers', 'fastapi', 'pydantic']
    print(f"\n📦 Checking key dependencies:")
    
    for dep in key_deps:
        try:
            module = importlib.import_module(dep)
            version = getattr(module, '__version__', 'Unknown')
            print(f"  ✅ {dep}: {version}")
        except ImportError:
            print(f"  ❌ {dep}: Not installed")
    
    input("\n🔍 Press Enter to see summary...")
    
    # Summary
    print_step("Summary", "What You Learned")
    
    print("""
🎯 Key Concepts Covered:
  • Package structure with __init__.py files
  • pyproject.toml vs requirements.txt
  • Import paths and module organization
  • Virtual environment importance
  • Dependency management

📚 Next Steps:
  1. Study the thai_model/__init__.py file
  2. Examine pyproject.toml sections in detail
  3. Practice creating your own package structure
  4. Install missing dependencies if needed

💡 Pro Tips:
  • Always use virtual environments for Python projects
  • Use 'python -m pip list' to see installed packages
  • Use 'python -c "import module; print(module.__file__)"' to find module locations
    
🚀 Ready for Module 1.2: Configuration Management!
""")

if __name__ == "__main__":
    main()
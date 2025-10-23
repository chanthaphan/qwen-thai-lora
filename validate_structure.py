#!/usr/bin/env python3
"""
Structure Validation Test
========================

Test script to validate the new project structure.
"""

import sys
from pathlib import Path
import importlib.util

def test_package_structure():
    """Test that the package structure is correct."""
    print("🧪 Testing Package Structure...")
    
    # Check main package
    main_package = Path("thai_model")
    if not main_package.exists():
        print("❌ Main package directory not found")
        return False
    
    # Check submodules
    required_modules = ["core", "api", "interfaces", "training", "utils"]
    for module in required_modules:
        module_path = main_package / module
        if not module_path.exists():
            print(f"❌ Module {module} not found")
            return False
        
        init_file = module_path / "__init__.py"
        if not init_file.exists():
            print(f"❌ __init__.py not found in {module}")
            return False
    
    print("✅ Package structure is correct")
    return True

def test_imports():
    """Test that imports work correctly."""
    print("🧪 Testing Imports...")
    
    try:
        # Test core imports
        sys.path.insert(0, str(Path.cwd()))
        
        # Test configuration import
        spec = importlib.util.spec_from_file_location(
            "config", "thai_model/core/config.py"
        )
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Create a ModelConfig instance
        model_config = config_module.ModelConfig()
        print(f"✅ ModelConfig created: {model_config.model_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration files."""
    print("🧪 Testing Configuration Files...")
    
    config_files = [
        "config/model_config.yaml",
        "config/training_config.yaml"
    ]
    
    for config_file in config_files:
        if not Path(config_file).exists():
            print(f"❌ Configuration file not found: {config_file}")
            return False
    
    print("✅ Configuration files exist")
    return True

def test_scripts():
    """Test script files."""
    print("🧪 Testing Script Files...")
    
    script_files = [
        "scripts/api_server.py"
    ]
    
    for script_file in script_files:
        script_path = Path(script_file)
        if not script_path.exists():
            print(f"❌ Script file not found: {script_file}")
            return False
        
        # Check if executable
        if not script_path.stat().st_mode & 0o111:
            print(f"⚠️  Script not executable: {script_file}")
    
    print("✅ Script files exist")
    return True

def test_deployment():
    """Test deployment files."""
    print("🧪 Testing Deployment Files...")
    
    deployment_files = [
        "deployment/docker/Dockerfile.cpu",
        "deployment/docker/docker-compose.yml",
        "pyproject.toml"
    ]
    
    for deploy_file in deployment_files:
        if not Path(deploy_file).exists():
            print(f"❌ Deployment file not found: {deploy_file}")
            return False
    
    print("✅ Deployment files exist")
    return True

def main():
    """Run all validation tests."""
    print("🔍 Validating Thai Language Model Project Structure")
    print("=" * 60)
    
    tests = [
        test_package_structure,
        test_imports, 
        test_configuration,
        test_scripts,
        test_deployment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 60)
    print("📋 Validation Summary:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("🎉 Project structure is valid and ready to use!")
        return 0
    else:
        print(f"❌ Some tests failed ({passed}/{total})")
        print("🔧 Please check the issues above and fix them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
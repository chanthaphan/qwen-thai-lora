#!/usr/bin/env python3
"""
Complete Test Runner
This script runs all available tests for the Thai model project
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def run_test(test_name, test_script, description):
    """Run a single test"""
    print(f"\n🧪 {test_name}")
    print("=" * 60)
    print(f"📋 {description}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # Change to project root directory
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        # Run the test
        result = subprocess.run([
            str(project_root / "llm-env/bin/python"),
            test_script
        ], capture_output=True, text=True, timeout=300)
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print("✅ PASSED")
            print(f"⏱️  Execution time: {execution_time:.2f}s")
            if result.stdout:
                # Show only last few lines to avoid clutter
                lines = result.stdout.strip().split('\n')
                if len(lines) > 10:
                    print("📄 Output (last 10 lines):")
                    for line in lines[-10:]:
                        print(f"   {line}")
                else:
                    print("📄 Output:")
                    for line in lines:
                        print(f"   {line}")
        else:
            print("❌ FAILED")
            print(f"⏱️  Execution time: {execution_time:.2f}s")
            if result.stderr:
                print("📄 Error output:")
                for line in result.stderr.strip().split('\n'):
                    print(f"   {line}")
        
        return result.returncode == 0, execution_time
        
    except subprocess.TimeoutExpired:
        print("❌ FAILED (Timeout)")
        return False, time.time() - start_time
    except Exception as e:
        print(f"❌ FAILED (Exception): {e}")
        return False, time.time() - start_time
    finally:
        os.chdir(original_cwd)

def main():
    """Main test runner"""
    print("🎯 Thai Model Test Suite")
    print("=" * 80)
    print("Running comprehensive tests for the Thai language model project")
    
    # Define all tests
    tests = [
        {
            "name": "Simple Model Test",
            "script": "src/testing/test_simple.py",
            "description": "Quick test to verify the model loads and generates text"
        },
        {
            "name": "Comprehensive Model Test",
            "script": "src/testing/test_model.py", 
            "description": "Detailed test with multiple Thai news articles"
        },
        {
            "name": "Model Evaluation",
            "script": "src/testing/evaluate_model.py",
            "description": "Performance evaluation with metrics and reporting"
        },
        {
            "name": "Streaming Connection Test",
            "script": "src/testing/test_streaming.py",
            "description": "Test connections to Ollama and vLLM servers"
        }
    ]
    
    # Run all tests
    results = []
    total_time = 0
    
    for test in tests:
        success, exec_time = run_test(
            test["name"],
            test["script"], 
            test["description"]
        )
        results.append((test["name"], success, exec_time))
        total_time += exec_time
        
        # Add a small delay between tests
        time.sleep(1)
    
    # Summary report
    print(f"\n📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"📈 Results: {passed}/{total} tests passed")
    print(f"⏱️  Total execution time: {total_time:.2f}s")
    
    print(f"\n📋 Individual Results:")
    for name, success, exec_time in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   • {name:<25} {status}  ({exec_time:.2f}s)")
    
    if passed == total:
        print(f"\n🎉 All tests passed! Your Thai model is working perfectly.")
        print(f"🚀 You can now deploy it using:")
        print(f"   • ./manage.sh chat-web    (Web interface)")
        print(f"   • ./manage.sh host-model  (API server)")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
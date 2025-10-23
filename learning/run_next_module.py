#!/usr/bin/env python3
"""
Run Next Learning Module
=======================

Script to run the next learning module and mark it as completed.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from learning.progress_tracker import LearningTracker

def main():
    print("🎓 Thai Model Learning Path - Next Module Runner")
    print("=" * 60)
    
    # Create tracker
    tracker = LearningTracker()
    
    # Show current progress
    print("\n📊 Current Progress:")
    tracker.show_progress()
    
    # Get completed modules
    completed_modules = set(tracker.progress.get("modules", {}).keys())
    
    # Define all modules with their file mappings
    all_modules = {
        "1.1": {
            "name": "Python Package Architecture", 
            "file": "module_1_1_package_architecture.py"
        },
        "1.2": {
            "name": "Configuration Management",
            "file": "module_1_2_configuration.py" 
        },
        "2.1": {
            "name": "Transformers & LoRA",
            "file": "module_2_1_transformers_lora.py"
        },
        "2.2": {
            "name": "Model Training & Fine-tuning",
            "file": "module_2_2_training.py"
        },
        "3.1": {
            "name": "FastAPI Fundamentals", 
            "file": "module_3_1_fastapi.py"
        },
        "3.2": {
            "name": "Advanced API Features",
            "file": "module_3_2_advanced_api.py"
        },
        "4.1": {
            "name": "Docker Mastery",
            "file": "module_4_1_docker.py"
        },
        "4.2": {
            "name": "Production Deployment",
            "file": "module_4_2_deployment.py"
        },
        "5.1": {
            "name": "Performance Optimization",
            "file": "module_5_1_performance_optimization.py"
        },
        "5.2": {
            "name": "Monitoring & Observability", 
            "file": "module_5_2_monitoring_observability.py"
        }
    }
    
    # Find next module
    next_module_id = None
    next_module_info = None
    
    for module_id, module_info in all_modules.items():
        if module_id not in completed_modules:
            next_module_id = module_id
            next_module_info = module_info
            break
    
    if not next_module_id:
        print("\n🎉 Congratulations! You've completed all modules!")
        print("🚀 You're ready to build amazing ML applications!")
        return
    
    print(f"\n🎯 Next Module: {next_module_id} - {next_module_info['name']}")
    
    # Check if module file exists
    module_file = Path(__file__).parent / next_module_info['file']
    if not module_file.exists():
        print(f"❌ Module file not found: {module_file}")
        print("💡 This module may need to be created.")
        return
    
    # Ask user if they want to run it
    choice = input(f"\n🚀 Run Module {next_module_id}? (y/N): ").strip().lower()
    
    if choice in ['y', 'yes']:
        print(f"\n🏃 Running Module {next_module_id}...")
        print("=" * 60)
        
        # Import and run the module
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("current_module", module_file)
            current_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(current_module)
            
            # Run the main function
            if hasattr(current_module, 'main'):
                current_module.main()
            
            # Ask if they want to mark it as completed
            completed = input(f"\n✅ Mark Module {next_module_id} as completed? (Y/n): ").strip().lower()
            
            if completed in ['', 'y', 'yes']:
                notes = input("📝 Add completion notes (optional): ").strip()
                tracker.complete_module(next_module_id, next_module_info['name'], notes)
                print(f"\n🎉 Module {next_module_id} marked as completed!")
                
                # Show updated progress
                print("\n📊 Updated Progress:")
                tracker.show_progress()
            
        except Exception as e:
            print(f"❌ Error running module: {e}")
    
    else:
        print("📚 You can run the module anytime with:")
        print(f"   python learning/{next_module_info['file']}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Learning Progress Tracker
========================

Track your progress through the Thai Model learning path.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class LearningTracker:
    def __init__(self):
        self.progress_file = Path(__file__).parent / "learning_progress.json"
        self.progress = self.load_progress()
    
    def load_progress(self) -> Dict:
        """Load progress from JSON file."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "started_date": datetime.now().isoformat(),
            "modules": {},
            "notes": []
        }
    
    def save_progress(self):
        """Save progress to JSON file."""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def complete_module(self, module_id: str, module_name: str, notes: str = ""):
        """Mark a module as completed."""
        self.progress["modules"][module_id] = {
            "name": module_name,
            "completed_date": datetime.now().isoformat(),
            "notes": notes
        }
        self.save_progress()
        print(f"✅ Module {module_id} completed: {module_name}")
    
    def add_note(self, note: str):
        """Add a learning note."""
        self.progress["notes"].append({
            "date": datetime.now().isoformat(),
            "note": note
        })
        self.save_progress()
        print(f"📝 Note added: {note}")
    
    def show_progress(self):
        """Display current progress."""
        print(f"\n{'='*60}")
        print(f"🎓 Thai Model Learning Progress")
        print(f"{'='*60}")
        
        started = datetime.fromisoformat(self.progress["started_date"])
        print(f"📅 Started: {started.strftime('%Y-%m-%d %H:%M')}")
        
        modules = self.progress.get("modules", {})
        print(f"📊 Completed Modules: {len(modules)}")
        
        if modules:
            print(f"\n✅ Completed Modules:")
            for module_id, info in modules.items():
                completed = datetime.fromisoformat(info["completed_date"])
                print(f"  • {module_id}: {info['name']}")
                print(f"    📅 {completed.strftime('%Y-%m-%d %H:%M')}")
                if info.get("notes"):
                    print(f"    📝 {info['notes']}")
        
        notes = self.progress.get("notes", [])
        if notes:
            print(f"\n📝 Learning Notes ({len(notes)}):")
            for note in notes[-5:]:  # Show last 5 notes
                note_date = datetime.fromisoformat(note["date"])
                print(f"  • {note_date.strftime('%m-%d %H:%M')}: {note['note']}")
        
        # Suggest next module
        completed_modules = set(modules.keys())
        all_modules = {
            "1.1": "Python Package Architecture",
            "1.2": "Configuration Management",
            "2.1": "Transformers & LoRA",
            "2.2": "Model Training & Fine-tuning",
            "3.1": "FastAPI Fundamentals",
            "3.2": "Advanced API Features",
            "4.1": "Docker Mastery",
            "4.2": "Production Deployment",
            "5.1": "Performance Optimization",
            "5.2": "Monitoring & Observability"
        }
        
        for module_id, module_name in all_modules.items():
            if module_id not in completed_modules:
                print(f"\n🎯 Next Suggested Module: {module_id} - {module_name}")
                break
        else:
            print(f"\n🎉 Congratulations! You've completed all modules!")

def main():
    tracker = LearningTracker()
    
    print("🎓 Thai Model Learning Tracker")
    print("=" * 40)
    print("1. Show progress")
    print("2. Complete module")
    print("3. Add note")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            tracker.show_progress()
        
        elif choice == "2":
            module_id = input("Module ID (e.g., 1.1): ").strip()
            module_name = input("Module name: ").strip()
            notes = input("Notes (optional): ").strip()
            tracker.complete_module(module_id, module_name, notes)
        
        elif choice == "3":
            note = input("Learning note: ").strip()
            tracker.add_note(note)
        
        elif choice == "4":
            print("👋 Happy learning!")
            break
        
        else:
            print("Invalid option. Please select 1-4.")

if __name__ == "__main__":
    main()
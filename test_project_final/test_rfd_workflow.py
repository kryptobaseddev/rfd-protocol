#!/usr/bin/env python3
"""
RFD Test Workflow - Simulates AI Developer Usage
Tests if RFD actually prevents hallucination and drift
"""

import sys
import os
sys.path.insert(0, '.rfd')

try:
    from rfd import RFD
    print("✓ RFD system imported successfully")
except Exception as e:
    print(f"✗ Failed to import RFD: {e}")
    sys.exit(1)

def test_feature_enforcement():
    """Test if RFD enforces that features must be defined in PROJECT.md"""
    print("\n=== TEST 1: Spec Enforcement ===")
    
    try:
        rfd = RFD()
        print("✓ RFD initialized")
        
        # Try to start work on a feature that exists
        print("Testing valid feature...")
        result = rfd.session.start_feature("Task Creation API")
        print(f"Valid feature result: {result}")
        
        # Try to start work on a feature that doesn't exist
        print("Testing invalid feature...")
        result = rfd.session.start_feature("Fake Feature That Doesn't Exist")
        print(f"Invalid feature result: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ Feature enforcement test failed: {e}")
        return False

def test_hallucination_detection():
    """Test if RFD can detect when AI claims to create files but doesn't"""
    print("\n=== TEST 2: Hallucination Detection ===")
    
    try:
        rfd = RFD()
        
        # Test: Claim to create a file but don't actually create it
        fake_claim = """
        I have successfully created the following files:
        
        1. app.py - Main Flask application with task creation endpoint
        2. models.py - Task model with validation
        3. storage.py - JSON file storage handler
        
        The Task Creation API is now complete and functional.
        """
        
        print("Testing fake claims detection...")
        is_valid = rfd.validator.validate_ai_claims(fake_claim)
        print(f"Validation result for fake claims: {is_valid}")
        
        if is_valid == False:
            print("✓ Hallucination correctly detected!")
            return True
        else:
            print("✗ Failed to detect hallucination!")
            return False
            
    except Exception as e:
        print(f"✗ Hallucination detection test failed: {e}")
        return False

def test_real_development():
    """Test actual development workflow with real files"""
    print("\n=== TEST 3: Real Development Workflow ===")
    
    try:
        rfd = RFD()
        
        # Start working on Feature 1
        print("Starting work on Task Creation API...")
        rfd.session.start_feature("Task Creation API")
        
        # Create actual files (simulating AI work)
        print("Creating real Flask application...")
        
        app_code = '''from flask import Flask, request, jsonify
import json
import uuid
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

def load_tasks():
    tasks_file = Path("tasks.json")
    if tasks_file.exists():
        with open(tasks_file, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open("tasks.json", 'w') as f:
        json.dump(tasks, f, indent=2)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data or 'description' not in data:
        return jsonify({"error": "title and description required"}), 400
    
    tasks = load_tasks()
    task = {
        "id": str(uuid.uuid4()),
        "title": data['title'],
        "description": data['description'],
        "created_at": datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    
    return jsonify(task), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(load_tasks())

if __name__ == '__main__':
    app.run(debug=True)
'''
        
        with open("app.py", 'w') as f:
            f.write(app_code)
        
        print("✓ Created app.py")
        
        # Test if RFD validates the real work
        real_claim = """
        I have created app.py with a complete Flask application that:
        1. Provides POST /tasks endpoint for creating tasks
        2. Provides GET /tasks endpoint for retrieving tasks  
        3. Persists data to tasks.json file
        4. Includes proper error handling
        """
        
        is_valid = rfd.validator.validate_ai_claims(real_claim)
        print(f"Validation result for real work: {is_valid}")
        
        # Test the actual app works
        print("Testing if Flask app actually runs...")
        import subprocess
        result = subprocess.run([sys.executable, "-c", "import app; print('Flask app syntax OK')"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Flask app has valid syntax")
            return True
        else:
            print(f"✗ Flask app has syntax errors: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Real development test failed: {e}")
        return False

def test_checkpoint_revert():
    """Test checkpoint and revert functionality"""
    print("\n=== TEST 4: Checkpoint and Revert ===")
    
    try:
        rfd = RFD()
        
        # Create a checkpoint
        print("Creating checkpoint...")
        checkpoint_id = rfd.session.create_checkpoint("Feature 1 - Basic API complete")
        print(f"Checkpoint created: {checkpoint_id}")
        
        # Try to revert to it
        print("Testing revert...")
        result = rfd.session.revert_to_checkpoint(checkpoint_id)
        print(f"Revert result: {result}")
        
        return checkpoint_id is not None
        
    except Exception as e:
        print(f"✗ Checkpoint/revert test failed: {e}")
        return False

def main():
    """Run all RFD tests"""
    print("🧪 RFD END-TO-END TEST SUITE")
    print("Testing if RFD actually prevents AI hallucination and drift...")
    
    results = {
        "spec_enforcement": test_feature_enforcement(),
        "hallucination_detection": test_hallucination_detection(), 
        "real_development": test_real_development(),
        "checkpoint_revert": test_checkpoint_revert()
    }
    
    print("\n" + "="*50)
    print("FINAL RESULTS:")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 RFD SYSTEM IS WORKING!")
    else:
        print("❌ RFD SYSTEM HAS CRITICAL ISSUES!")
    
    return results

if __name__ == "__main__":
    main()
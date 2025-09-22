#!/usr/bin/env python3
"""
RFD-2 SIMPLIFIED REALITY TEST
Using the working .rfd implementation to test core functionality
"""

import sys
import os
import json
from pathlib import Path

# Use the working .rfd implementation
sys.path.insert(0, '.rfd')

def test_basic_functionality():
    """Test basic RFD functionality that's known to work"""
    print("🧪 SIMPLIFIED RFD REALITY TEST")
    print("Testing core functionality with working implementation...")
    
    results = {}
    
    # Test 1: Basic import and initialization
    print("\n=== TEST 1: Basic Import & Init ===")
    try:
        from rfd import RFD
        rfd = RFD()
        print("✓ RFD imports and initializes")
        results["basic_init"] = True
    except Exception as e:
        print(f"✗ Basic init failed: {e}")
        results["basic_init"] = False
        return results
    
    # Test 2: ValidationEngine hallucination detection
    print("\n=== TEST 2: Hallucination Detection ===")
    try:
        # Test fake file claims
        fake_claim = "I created nonexistent_file.py with function fake_function()"
        passed, details = rfd.validator.validate_ai_claims(fake_claim)
        
        if not passed:
            print("✓ Correctly detected fake file claim")
            results["hallucination_detection"] = True
        else:
            print("✗ Failed to detect fake file claim")
            results["hallucination_detection"] = False
            
    except Exception as e:
        print(f"✗ Hallucination detection failed: {e}")
        results["hallucination_detection"] = False
    
    # Test 3: Real file validation
    print("\n=== TEST 3: Real File Validation ===")
    try:
        # Create a real file
        with open("test_file.py", 'w') as f:
            f.write("def test_function():\n    return 'test'\n")
        
        real_claim = "I created test_file.py with function test_function()"
        passed, details = rfd.validator.validate_ai_claims(real_claim)
        
        if passed:
            print("✓ Correctly validated real file claim")
            results["real_validation"] = True
        else:
            print("✗ False negative on real file claim")
            results["real_validation"] = False
        
        # Clean up
        os.remove("test_file.py")
        
    except Exception as e:
        print(f"✗ Real file validation failed: {e}")
        results["real_validation"] = False
    
    # Test 4: Session management
    print("\n=== TEST 4: Session Management ===")
    try:
        session_id = rfd.session.start("test_feature")
        current = rfd.session.get_current()
        rfd.session.end(success=True)
        
        if session_id and current:
            print("✓ Session management works")
            results["session_management"] = True
        else:
            print("✗ Session management issues")
            results["session_management"] = False
            
    except Exception as e:
        print(f"✗ Session management failed: {e}")
        results["session_management"] = False
    
    return results

def test_realistic_workflow():
    """Test a realistic development workflow"""
    print("\n=== WORKFLOW TEST: Simulate Real Development ===")
    
    workflow_results = {}
    
    try:
        from rfd import RFD
        rfd = RFD()
        
        # Scenario: AI claims to build a simple Flask app
        print("\nScenario: AI builds Task Creation API...")
        
        # Step 1: AI claims to create files (but lies)
        fake_claim = """
        I have implemented the Task Creation API with:
        
        1. app.py - Main Flask application
        2. models.py - Task model with validation  
        3. storage.py - JSON file storage
        4. tests.py - Unit tests
        
        The API is now complete and ready for testing.
        """
        
        print("Testing AI claim validation...")
        passed, details = rfd.validator.validate_ai_claims(fake_claim)
        
        if not passed:
            print("✓ RFD caught the AI lie - no files were created")
            workflow_results["catch_lies"] = True
        else:
            print("✗ RFD failed to catch AI lie")
            workflow_results["catch_lies"] = False
        
        # Step 2: Now create real files and test again
        print("\nAI actually creates the files...")
        
        # Create app.py
        app_code = '''
from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    task = {
        "id": len(load_tasks()) + 1,
        "title": data["title"],
        "created_at": datetime.now().isoformat()
    }
    save_task(task)
    return jsonify(task)

def load_tasks():
    try:
        with open("tasks.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_task(task):
    tasks = load_tasks()
    tasks.append(task)
    with open("tasks.json", "w") as f:
        json.dump(tasks, f)

if __name__ == "__main__":
    app.run()
'''
        
        with open("app.py", 'w') as f:
            f.write(app_code)
        
        # Create models.py
        with open("models.py", 'w') as f:
            f.write("class Task:\n    def __init__(self, title):\n        self.title = title\n")
        
        # Test real claim
        real_claim = """
        I have implemented:
        - app.py with create_task endpoint
        - models.py with Task class
        """
        
        passed, details = rfd.validator.validate_ai_claims(real_claim)
        
        if passed:
            print("✓ RFD correctly validated real implementation")
            workflow_results["validate_real"] = True
        else:
            print("✗ RFD incorrectly rejected real implementation")
            workflow_results["validate_real"] = False
        
        # Test if code actually runs
        try:
            compile(open("app.py").read(), "app.py", "exec")
            print("✓ Generated code compiles successfully")
            workflow_results["code_quality"] = True
        except SyntaxError:
            print("✗ Generated code has syntax errors")
            workflow_results["code_quality"] = False
        
        # Clean up
        for file in ["app.py", "models.py", "tasks.json"]:
            if os.path.exists(file):
                os.remove(file)
        
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        workflow_results = {"error": str(e)}
    
    return workflow_results

def generate_final_report():
    """Generate final report comparing claims vs reality"""
    print("\n" + "="*60)
    print("RFD-2 FINAL TEST REPORT")
    print("="*60)
    
    # Run all tests
    basic_results = test_basic_functionality()
    workflow_results = test_realistic_workflow()
    
    # Calculate overall metrics
    all_tests = {**basic_results, **workflow_results}
    passed_tests = sum(1 for result in all_tests.values() if result is True)
    total_tests = len(all_tests)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\nOVERALL RESULTS:")
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\nDETAILED RESULTS:")
    for test_name, result in all_tests.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    # Final verdict
    print(f"\n" + "="*60)
    if success_rate >= 90:
        verdict = "✅ RFD IS WORKING - READY FOR PRODUCTION"
        recommendation = "Ship v1.0 with confidence"
    elif success_rate >= 70:
        verdict = "⚠️ RFD MOSTLY WORKS - NEEDS MINOR FIXES"
        recommendation = "Fix remaining issues before v1.0"
    else:
        verdict = "❌ RFD HAS CRITICAL ISSUES"
        recommendation = "Major fixes needed before release"
    
    print(f"VERDICT: {verdict}")
    print(f"RECOMMENDATION: {recommendation}")
    
    # Cross-check with conflicting reports
    print(f"\n" + "="*60)
    print("CROSS-CHECK WITH EXISTING REPORTS:")
    print("="*60)
    
    print("RFD-Main Report: 91% ready for v1.0")
    print("RFD-4 Bug Report: 60% effective, critical bugs")
    print(f"RFD-2 Reality Test: {success_rate:.1f}% effective")
    
    if success_rate >= 80:
        print("\n✓ RFD-2 test SUPPORTS RFD-Main optimism")
    else:
        print("\n✓ RFD-2 test SUPPORTS RFD-4 concerns")
    
    return {
        "success_rate": success_rate,
        "verdict": verdict,
        "recommendation": recommendation,
        "detailed_results": all_tests
    }

def main():
    """Main test execution"""
    report = generate_final_report()
    
    # Save report
    with open("../RFD-2-FINAL-TEST-REPORT.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    main()
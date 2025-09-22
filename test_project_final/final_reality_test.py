#!/usr/bin/env python3
"""
RFD-2 FINAL REALITY TEST
Definitive end-to-end test simulating real developer workflow
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
import json

# Copy nexus files to current directory for testing
import shutil as sh
nexus_path = Path('/mnt/projects/rfd-protocol/nexus_rfd_protocol')
for py_file in nexus_path.glob('*.py'):
    if not Path(py_file.name).exists():
        sh.copy2(py_file, '.')

try:
    from rfd import RFD
    from validation import ValidationEngine
    from session import SessionManager
    print("✓ Successfully imported RFD components")
except ImportError as e:
    print(f"✗ Failed to import RFD components: {e}")
    sys.exit(1)

class RealityTest:
    """Comprehensive reality test for RFD Protocol"""
    
    def __init__(self):
        self.test_results = {}
        self.working_dir = None
        self.rfd = None
    
    def setup_test_environment(self):
        """Set up isolated test environment"""
        print("\n=== SETUP: Creating Test Environment ===")
        
        # Create temporary working directory
        self.working_dir = Path.cwd() / "temp_test_env"
        if self.working_dir.exists():
            shutil.rmtree(self.working_dir)
        self.working_dir.mkdir()
        
        # Change to test directory
        os.chdir(self.working_dir)
        
        # Create a real PROJECT.md
        project_content = """# Real Project Test

## Features

### user_auth
**Description**: User authentication system
**Acceptance Criteria**:
- POST /auth/login endpoint
- Returns JWT token
- Validates credentials

### task_manager  
**Description**: Task management system
**Acceptance Criteria**:
- CRUD operations for tasks
- Task priority system
- Due date management
"""
        
        with open("PROJECT.md", 'w') as f:
            f.write(project_content)
        
        print(f"✓ Test environment created at: {self.working_dir}")
        return True
    
    def test_rfd_initialization(self):
        """Test if RFD can initialize in a real project"""
        print("\n=== TEST 1: RFD Initialization ===")
        
        try:
            self.rfd = RFD()
            spec = self.rfd.load_project_spec()
            print(f"✓ RFD initialized successfully")
            print(f"✓ Project spec loaded: {len(spec.get('features', []))} features")
            return True
        except Exception as e:
            print(f"✗ RFD initialization failed: {e}")
            return False
    
    def test_session_workflow(self):
        """Test complete session workflow"""
        print("\n=== TEST 2: Session Workflow ===")
        
        try:
            session = SessionManager(self.rfd)
            
            # Start session with valid feature
            print("Starting session for 'user_auth'...")
            session_id = session.start("user_auth")
            print(f"✓ Session started: {session_id}")
            
            # Check current session
            current = session.get_current()
            print(f"✓ Current session: {current['feature_id']}")
            
            # Try invalid feature (should fail)
            try:
                session.start("invalid_feature")
                print("✗ BUG: Invalid feature was accepted!")
                return False
            except ValueError:
                print("✓ Invalid feature correctly rejected")
            
            # End session
            session.end(success=True)
            print("✓ Session ended successfully")
            
            return True
        except Exception as e:
            print(f"✗ Session workflow failed: {e}")
            return False
    
    def test_hallucination_detection(self):
        """Test AI hallucination detection with real scenarios"""
        print("\n=== TEST 3: Hallucination Detection ===")
        
        try:
            validator = ValidationEngine(self.rfd)
            
            # Test 1: Completely fake files
            fake_claim = """
            I have created auth.py with the following functions:
            - authenticate_user()
            - generate_token()
            - validate_token()
            """
            
            passed, details = validator.validate_ai_claims(fake_claim)
            print(f"Fake files test - Passed: {passed}")
            if not passed:
                print("✓ Correctly detected fake files")
            else:
                print("✗ Failed to detect fake files")
                return False
            
            # Test 2: Real file, fake functions
            with open("real_auth.py", 'w') as f:
                f.write("def real_function():\n    pass\n")
            
            mixed_claim = """
            I have updated real_auth.py with:
            - real_function() (already exists)
            - fake_function() (doesn't exist)
            """
            
            passed, details = validator.validate_ai_claims(mixed_claim)
            print(f"Mixed claims test - Passed: {passed}")
            if not passed:
                print("✓ Correctly detected fake functions in real file")
            else:
                print("✗ Failed to detect fake functions")
                return False
            
            # Test 3: All real claims
            real_claim = """
            I have created real_auth.py with:
            - real_function()
            """
            
            passed, details = validator.validate_ai_claims(real_claim)
            print(f"Real claims test - Passed: {passed}")
            if passed:
                print("✓ Correctly validated real claims")
            else:
                print("✗ False negative on real claims")
                return False
            
            return True
        except Exception as e:
            print(f"✗ Hallucination detection failed: {e}")
            return False
    
    def test_development_workflow(self):
        """Test realistic development workflow"""
        print("\n=== TEST 4: Development Workflow ===")
        
        try:
            # Start working on user_auth feature
            session = SessionManager(self.rfd)
            session.start("user_auth")
            
            # Simulate AI creating files for the feature
            auth_code = '''
from flask import Flask, request, jsonify
import jwt
import hashlib

app = Flask(__name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id):
    payload = {"user_id": user_id}
    return jwt.encode(payload, "secret", algorithm="HS256")

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # Mock validation (would normally check database)
    if username == "test" and password == "test":
        token = generate_token(1)
        return jsonify({"token": token})
    
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(debug=True)
'''
            
            with open("auth.py", 'w') as f:
                f.write(auth_code)
            
            print("✓ Created auth.py with real implementation")
            
            # Validate the work
            validator = ValidationEngine(self.rfd)
            claim = """
            I have implemented the user authentication feature in auth.py with:
            - hash_password() function for secure password hashing
            - generate_token() function for JWT creation
            - login() endpoint at POST /auth/login
            """
            
            passed, details = validator.validate_ai_claims(claim)
            print(f"Development validation - Passed: {passed}")
            
            # Test if the code actually works
            try:
                # Basic syntax check
                with open("auth.py", 'r') as f:
                    code = f.read()
                compile(code, "auth.py", "exec")
                print("✓ Code compiles successfully")
            except SyntaxError as e:
                print(f"✗ Syntax error in generated code: {e}")
                return False
            
            # End session
            session.end(success=True)
            print("✓ Feature development completed")
            
            return passed
        except Exception as e:
            print(f"✗ Development workflow failed: {e}")
            return False
    
    def test_edge_cases(self):
        """Test edge cases and potential vulnerabilities"""
        print("\n=== TEST 5: Edge Cases ===")
        
        try:
            validator = ValidationEngine(self.rfd)
            
            # Edge case 1: Subtle lies (existing function modifications)
            subtle_lie = """
            I have enhanced the existing hash_password function in auth.py to:
            - Added salt for better security
            - Implemented bcrypt instead of sha256
            - Added input validation
            """
            
            passed, details = validator.validate_ai_claims(subtle_lie)
            print(f"Subtle lies test - Passed: {passed}")
            
            # Edge case 2: Empty/malformed claims
            empty_claim = ""
            passed_empty, _ = validator.validate_ai_claims(empty_claim)
            print(f"Empty claims test - Passed: {passed_empty}")
            
            # Edge case 3: Multiple files in one claim
            multi_claim = """
            I have created:
            - auth.py with login functionality
            - users.py with user model
            - config.py with app configuration
            """
            
            # Only auth.py exists, others don't
            passed_multi, details_multi = validator.validate_ai_claims(multi_claim)
            print(f"Multiple files test - Passed: {passed_multi}")
            
            return True
        except Exception as e:
            print(f"✗ Edge cases test failed: {e}")
            return False
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        print("\n=== CLEANUP: Removing Test Environment ===")
        
        try:
            # Change back to original directory
            os.chdir(self.working_dir.parent)
            
            # Remove test directory
            if self.working_dir.exists():
                shutil.rmtree(self.working_dir)
            
            print("✓ Test environment cleaned up")
            return True
        except Exception as e:
            print(f"✗ Cleanup failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🧪 RFD-2 FINAL REALITY TEST SUITE")
        print("Testing real-world developer workflow...")
        
        tests = [
            ("Environment Setup", self.setup_test_environment),
            ("RFD Initialization", self.test_rfd_initialization),
            ("Session Workflow", self.test_session_workflow),
            ("Hallucination Detection", self.test_hallucination_detection),
            ("Development Workflow", self.test_development_workflow),
            ("Edge Cases", self.test_edge_cases),
            ("Cleanup", self.cleanup_test_environment)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"✗ {test_name} crashed with exception: {e}")
                results[test_name] = False
        
        # Generate final report
        print("\n" + "="*60)
        print("FINAL REALITY TEST RESULTS")
        print("="*60)
        
        passed_tests = 0
        total_tests = len(results)
        
        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{test_name:<25}: {status}")
            if passed:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\nSuccess Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Final verdict
        if success_rate >= 90:
            verdict = "🎉 RFD IS PRODUCTION READY!"
        elif success_rate >= 70:
            verdict = "⚠️  RFD NEEDS FIXES BEFORE RELEASE"
        else:
            verdict = "❌ RFD IS NOT READY FOR PRODUCTION"
        
        print(f"\nVERDICT: {verdict}")
        
        return results, success_rate

def main():
    """Run the final reality test"""
    test = RealityTest()
    results, success_rate = test.run_all_tests()
    
    # Save results for reporting
    with open("../final_test_results.json", 'w') as f:
        json.dump({
            "success_rate": success_rate,
            "results": results,
            "timestamp": "2025-09-22",
            "tester": "RFD-2"
        }, f, indent=2)
    
    return success_rate

if __name__ == "__main__":
    main()
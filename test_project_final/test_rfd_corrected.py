#!/usr/bin/env python3
"""
Corrected RFD Test - Uses actual API methods
"""

import sys
import os
sys.path.insert(0, '.rfd')

def test_basic_initialization():
    """Test if RFD can be imported and initialized"""
    print("\n=== TEST 1: Basic Initialization ===")
    
    try:
        from rfd import RFD
        rfd = RFD()
        print("✓ RFD initialized successfully")
        print(f"  - RFD root: {rfd.root}")
        print(f"  - RFD dir: {rfd.rfd_dir}")
        print(f"  - Database: {rfd.db_path}")
        return True, rfd
    except Exception as e:
        print(f"✗ RFD initialization failed: {e}")
        return False, None

def test_session_manager(rfd):
    """Test SessionManager functionality"""
    print("\n=== TEST 2: Session Manager ===")
    
    try:
        # Test starting a session (need to provide feature_id)
        print("Testing session start...")
        session_id = rfd.session.start("test_feature")
        print(f"✓ Session started with ID: {session_id}")
        
        # Test getting current session
        current = rfd.session.get_current()
        print(f"✓ Current session: {current}")
        
        # Test ending session
        rfd.session.end(success=True)
        print("✓ Session ended successfully")
        
        return True
    except Exception as e:
        print(f"✗ Session manager test failed: {e}")
        return False

def test_hallucination_detection(rfd):
    """Test ValidationEngine hallucination detection"""
    print("\n=== TEST 3: Hallucination Detection ===")
    
    try:
        # Test with fake claims (files that don't exist)
        fake_claim = """
        I have created the following files:
        - nonexistent_file.py with class TaskManager
        - fake_app.py with function create_task()
        - missing.py with the main application logic
        """
        
        print("Testing fake claims...")
        passed, details = rfd.validator.validate_ai_claims(fake_claim)
        print(f"Validation passed: {passed}")
        print("Details:")
        for detail in details:
            print(f"  - {detail}")
        
        if not passed:
            print("✓ Correctly detected hallucination!")
            return True
        else:
            print("✗ Failed to detect hallucination!")
            return False
            
    except Exception as e:
        print(f"✗ Hallucination detection failed: {e}")
        return False

def test_real_file_validation(rfd):
    """Test validation with real files"""
    print("\n=== TEST 4: Real File Validation ===")
    
    try:
        # Create a real file
        with open("test_real.py", 'w') as f:
            f.write("""
def hello_world():
    print("Hello, World!")

class TestClass:
    def test_method(self):
        return "test"
""")
        
        print("✓ Created test_real.py")
        
        # Test validation with real claims
        real_claim = """
        I have created test_real.py with:
        - function hello_world()
        - class TestClass
        """
        
        passed, details = rfd.validator.validate_ai_claims(real_claim)
        print(f"Real file validation passed: {passed}")
        print("Details:")
        for detail in details:
            print(f"  - {detail}")
        
        # Clean up
        os.remove("test_real.py")
        
        return passed
        
    except Exception as e:
        print(f"✗ Real file validation failed: {e}")
        return False

def test_build_engine(rfd):
    """Test BuildEngine functionality"""
    print("\n=== TEST 5: Build Engine ===")
    
    try:
        # Test build detection
        result = rfd.builder.build()
        print(f"Build result: {result}")
        return True
    except Exception as e:
        print(f"✗ Build engine test failed: {e}")
        return False

def test_spec_engine(rfd):
    """Test SpecEngine functionality"""
    print("\n=== TEST 6: Spec Engine ===")
    
    try:
        # Test spec parsing
        spec_status = rfd.spec.validate()
        print(f"Spec validation: {spec_status}")
        return True
    except Exception as e:
        print(f"✗ Spec engine test failed: {e}")
        return False

def main():
    """Run corrected RFD tests using actual API"""
    print("🧪 CORRECTED RFD TEST SUITE")
    print("Testing actual RFD implementation...")
    
    # Basic initialization
    init_success, rfd = test_basic_initialization()
    if not init_success:
        print("❌ Cannot proceed without RFD initialization")
        return
    
    tests = [
        ("Session Manager", lambda: test_session_manager(rfd)),
        ("Hallucination Detection", lambda: test_hallucination_detection(rfd)),
        ("Real File Validation", lambda: test_real_file_validation(rfd)),
        ("Build Engine", lambda: test_build_engine(rfd)),
        ("Spec Engine", lambda: test_spec_engine(rfd))
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n" + "="*50)
    print("CORRECTED TEST RESULTS:")
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nSuccess Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    return results

if __name__ == "__main__":
    main()
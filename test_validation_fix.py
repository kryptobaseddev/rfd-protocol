#!/usr/bin/env python3
"""
Test script to verify ValidationEngine can catch AI hallucinations
"""

import sys
import os
sys.path.insert(0, '.rfd')

from validation import ValidationEngine
from pathlib import Path

class MockRFD:
    """Mock RFD object for testing"""
    def __init__(self):
        pass
    
    def load_project_spec(self):
        return {
            'rules': {},
            'features': []
        }

def test_ai_hallucination_detection():
    """Test that ValidationEngine catches when AI lies about creating files/functions"""
    
    # Create a ValidationEngine instance
    rfd = MockRFD()
    validator = ValidationEngine(rfd)
    
    print("=" * 60)
    print("TESTING VALIDATION ENGINE - AI HALLUCINATION DETECTION")
    print("=" * 60)
    
    # Test 1: AI claims it created files that don't exist
    print("\n[TEST 1] AI claims to have created non-existent files:")
    fake_claims = """
    I've successfully created the following files:
    - Created file super_awesome_module.py with the main application logic
    - Wrote database_handler.py to handle all database operations
    - Created test_everything.py with comprehensive tests
    - File config.json was created with all configuration
    """
    
    passed, results = validator.validate_ai_claims(fake_claims)
    
    print(f"\nClaim: AI says it created 4 files")
    print("Results:")
    for result in results:
        if result['type'] == 'file':
            status = "✅" if result['exists'] else "❌"
            print(f"  {status} {result['message']}")
    
    print(f"\nValidation passed: {passed}")
    assert passed == False, "Should fail - files don't exist!"
    print("✅ CORRECT: ValidationEngine detected AI lying about files!")
    
    # Test 2: AI claims it created functions that don't exist
    print("\n" + "=" * 60)
    print("[TEST 2] AI claims to have created non-existent functions:")
    fake_claims2 = """
    I've implemented the following functions:
    - Function process_data() to handle data processing
    - Created class DataManager for managing the database
    - Implemented method calculate_metrics() for analytics
    - Added function super_duper_function() in validation.py
    """
    
    passed2, results2 = validator.validate_ai_claims(fake_claims2)
    
    print(f"\nClaim: AI says it created 4 functions/classes")
    print("Results:")
    for result in results2:
        if result['type'] == 'function':
            status = "✅" if result['exists'] else "❌"
            print(f"  {status} {result['message']}")
    
    print(f"\nValidation passed: {passed2}")
    assert passed2 == False, "Should fail - most functions don't exist!"
    print("✅ CORRECT: ValidationEngine detected AI lying about functions!")
    
    # Test 3: Mix of real and fake claims (ValidationEngine itself exists)
    print("\n" + "=" * 60)
    print("[TEST 3] Mix of real and fake claims:")
    mixed_claims = """
    I've created the following:
    - Created file .rfd/validation.py with ValidationEngine class
    - Added function validate_ai_claims() to check AI output
    - Created file magical_unicorn.py with rainbow functions
    - Implemented class ValidationEngine in validation.py
    - Added function make_coffee() to handle coffee brewing
    """
    
    passed3, results3 = validator.validate_ai_claims(mixed_claims)
    
    print(f"\nClaim: Mix of real and fake items")
    print("Results:")
    for result in results3:
        status = "✅" if result['exists'] else "❌"
        print(f"  {status} {result['message']}")
    
    print(f"\nValidation passed: {passed3}")
    assert passed3 == False, "Should fail - contains false claims!"
    print("✅ CORRECT: ValidationEngine detected mixed truth/lies!")
    
    # Test 4: All true claims
    print("\n" + "=" * 60)
    print("[TEST 4] All true claims (ValidationEngine components):")
    true_claims = """
    The ValidationEngine has been updated with:
    - Method validate_ai_claims() to validate AI output
    - Class ValidationEngine exists in .rfd/validation.py
    - Function _verify_function_exists to check functions
    - Method _extract_file_claims to parse file mentions
    """
    
    passed4, results4 = validator.validate_ai_claims(true_claims)
    
    print(f"\nClaim: Real components that exist")
    print("Results:")
    for result in results4:
        status = "✅" if result['exists'] else "❌"
        print(f"  {status} {result['message']}")
    
    print(f"\nValidation passed: {passed4}")
    assert passed4 == True, "Should pass - all claims are true!"
    print("✅ CORRECT: ValidationEngine correctly validates true claims!")
    
    print("\n" + "=" * 60)
    print("🎯 ALL TESTS PASSED!")
    print("ValidationEngine NOW CATCHES AI HALLUCINATIONS!")
    print("=" * 60)

if __name__ == "__main__":
    test_ai_hallucination_detection()
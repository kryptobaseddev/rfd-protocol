#!/usr/bin/env python3
"""
End-to-end validation test
Tests if RFD catches AI lies in real scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nexus_rfd_protocol.validation import ValidationEngine
from nexus_rfd_protocol.rfd import RFD

def test_real_end_to_end():
    """Test real end-to-end scenario"""
    print("=== END-TO-END VALIDATION TEST ===")
    
    rfd = RFD()
    validator = ValidationEngine(rfd)
    
    # Simulate AI claims about what it created
    fake_claims = [
        # These are LIES - the AI claims to create things that don't exist
        "I created a comprehensive web API in fake_ai_claim.py with the following functions: create_user(), delete_user(), update_user(), get_all_users(), and authenticate_user()",
        "Added database connection with PostgreSQL to the simple_function",
        "Implemented advanced error handling throughout fake_ai_claim.py",
        "Created FastAPI endpoints in fake_ai_claim.py for REST API",
        "Added async/await pattern to all functions for better performance",
    ]
    
    real_claims = [
        # These should PASS - they're true
        "Created function simple_function in fake_ai_claim.py",
        "I have implemented a basic function that returns a string",
    ]
    
    print("\nTesting FAKE claims (should be caught as lies):")
    fake_caught = 0
    for claim in fake_claims:
        passed, details = validator.validate_ai_claims(claim)
        if not passed:
            print(f"✅ CAUGHT LIE: {claim[:50]}...")
            fake_caught += 1
        else:
            print(f"❌ MISSED LIE: {claim[:50]}...")
            
    print(f"\nLie detection rate: {fake_caught}/{len(fake_claims)} = {fake_caught/len(fake_claims)*100:.1f}%")
    
    print("\nTesting REAL claims (should pass):")
    real_passed = 0
    for claim in real_claims:
        passed, details = validator.validate_ai_claims(claim)
        if passed:
            print(f"✅ VALIDATED: {claim[:50]}...")
            real_passed += 1
        else:
            print(f"❌ FALSE NEGATIVE: {claim[:50]}...")
            
    print(f"\nValid claim acceptance rate: {real_passed}/{len(real_claims)} = {real_passed/len(real_claims)*100:.1f}%")
    
    # Overall assessment
    lie_detection_good = (fake_caught / len(fake_claims)) >= 0.8
    valid_acceptance_good = (real_passed / len(real_claims)) >= 0.8
    
    if lie_detection_good and valid_acceptance_good:
        print("\n🎉 END-TO-END TEST PASSED - RFD validation works!")
        return True
    else:
        print("\n❌ END-TO-END TEST FAILED - RFD validation has issues!")
        return False

if __name__ == "__main__":
    success = test_real_end_to_end()
    sys.exit(0 if success else 1)
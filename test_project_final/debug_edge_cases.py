#!/usr/bin/env python3

from validation import ValidationEngine
from rfd import RFD
from pathlib import Path

rfd = RFD()
validator = ValidationEngine(rfd)

# Test 1: Subtle lies - claiming to enhance non-existent function
subtle_lie = """
I have enhanced the existing hash_password function in auth.py to:
- Added salt for better security
- Implemented bcrypt instead of sha256
- Added input validation
"""

print("TESTING SUBTLE LIES:")
print("Claim text:")
print(subtle_lie)
print("\n" + "="*50)

passed, details = validator.validate_ai_claims(subtle_lie)

print(f"Overall passed: {passed} (SHOULD BE FALSE)")
print("\nDetailed results:")
for detail in details:
    print(f"  {detail['type']}: {detail['target']} -> {detail['exists']} ({detail['message']})")

# Debug extraction
print("\n" + "="*50)
print("DEBUG: Function extraction")
function_claims = validator._extract_function_claims(subtle_lie)
print(f"Extracted functions: {function_claims}")

print("\nDEBUG: File extraction")
file_claims = validator._extract_file_claims(subtle_lie)
print(f"Extracted files: {file_claims}")

print("\nDEBUG: Modification extraction")
modification_claims = validator._extract_modification_claims(subtle_lie)
print(f"Extracted modifications: {modification_claims}")
#!/usr/bin/env python3

from validation import ValidationEngine
from rfd import RFD
from pathlib import Path

# Create test setup
Path("real_auth.py").write_text("def real_function():\n    pass\n")

rfd = RFD()
validator = ValidationEngine(rfd)

mixed_claim = """
I have updated real_auth.py with:
- real_function() (already exists)
- fake_function() (doesn't exist)
"""

print("Testing mixed claim...")
print("Claim text:")
print(mixed_claim)
print("\n" + "="*50)

passed, details = validator.validate_ai_claims(mixed_claim)

print(f"Overall passed: {passed}")
print("\nDetailed results:")
for detail in details:
    print(f"  {detail['type']}: {detail['target']} -> {detail['exists']} ({detail['message']})")

# Let's also debug the extraction process
print("\n" + "="*50)
print("DEBUG: Function extraction")
function_claims = validator._extract_function_claims(mixed_claim)
print(f"Extracted functions: {function_claims}")

print("\nDEBUG: File extraction")
file_claims = validator._extract_file_claims(mixed_claim)
print(f"Extracted files: {file_claims}")

print("\nDEBUG: Modification extraction")
modification_claims = validator._extract_modification_claims(mixed_claim)
print(f"Extracted modifications: {modification_claims}")

# Manual verification
print("\nMANUAL VERIFICATION:")
for func_name, file_hint in function_claims:
    exists = validator._verify_function_exists(func_name, file_hint)
    print(f"  Function '{func_name}' exists: {exists}")

# Clean up
Path("real_auth.py").unlink()
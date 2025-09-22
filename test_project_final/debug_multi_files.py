#!/usr/bin/env python3

from validation import ValidationEngine
from rfd import RFD
from pathlib import Path

rfd = RFD()
validator = ValidationEngine(rfd)

# Create only one of the claimed files
Path("auth.py").write_text("def login():\n    pass\n")

# Test multiple files claim
multi_claim = """
I have created:
- auth.py with login functionality
- users.py with user model
- config.py with app configuration
"""

print("TESTING MULTIPLE FILES CLAIM:")
print("Claim text:")
print(multi_claim)
print("\nFiles that actually exist:")
for file in ["auth.py", "users.py", "config.py"]:
    exists = Path(file).exists()
    print(f"  {file}: {'EXISTS' if exists else 'MISSING'}")

print("\n" + "="*50)

passed, details = validator.validate_ai_claims(multi_claim)

print(f"Overall passed: {passed} (SHOULD BE FALSE - some files missing)")
print("\nDetailed results:")
for detail in details:
    print(f"  {detail['type']}: {detail['target']} -> {detail['exists']} ({detail['message']})")

# Debug extraction
print("\n" + "="*50)
print("DEBUG: File extraction")
file_claims = validator._extract_file_claims(multi_claim)
print(f"Extracted files: {file_claims}")

print("\nDEBUG: Function extraction")
function_claims = validator._extract_function_claims(multi_claim)
print(f"Extracted functions: {function_claims}")

# Clean up
Path("auth.py").unlink()
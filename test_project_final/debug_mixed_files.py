#!/usr/bin/env python3

from validation import ValidationEngine
from rfd import RFD
from pathlib import Path

# Setup
Path("auth.py").write_text("def login(): pass")

rfd = RFD()
validator = ValidationEngine(rfd)

claim = "I created auth.py and users.py with full functionality"

print("DEBUGGING MIXED REAL/FAKE FILES:")
print(f"Claim: {claim}")
print("\nFiles that exist:")
for f in ["auth.py", "users.py"]:
    exists = Path(f).exists()
    print(f"  {f}: {'EXISTS' if exists else 'MISSING'}")

passed, details = validator.validate_ai_claims(claim)

print(f"\nResult: {passed} (SHOULD BE FALSE)")
print("\nDetailed results:")
for detail in details:
    print(f"  {detail['type']}: {detail['target']} -> {detail['exists']} ({detail['message']})")

# Debug extractions
print("\nFile claims:", validator._extract_file_claims(claim))
print("Function claims:", validator._extract_function_claims(claim))

# Cleanup
Path("auth.py").unlink()
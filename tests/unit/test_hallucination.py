#!/usr/bin/env python
"""Test hallucination detection by making false claims"""

from rfd.validation import ValidationEngine
from rfd.rfd import RFD

# Create RFD instance and ValidationEngine
rfd = RFD()
ve = ValidationEngine(rfd)

# Make a false claim
false_claim = "Created /mnt/projects/rfd-protocol/totally_fake_file.py with function magic_function()"
result, details = ve.validate_ai_claims(false_claim)
print(f"False claim test: {'PASS - Caught hallucination!' if not result else 'FAIL - Missed hallucination'}")
if details:
    for detail in details:
        print(f"  - {detail['message']}")

# Test 2: True claim about existing file  
true_claim = "Created test_hallucination.py with imports"
result, details = ve.validate_ai_claims(true_claim)
print(f"True claim test: {'PASS - Recognized truth' if result else 'FAIL - False positive'}")
if details:
    for detail in details:
        print(f"  - {detail['message']}")

# Test 3: Mixed claims
mixed_claim = """
Created test_hallucination.py with ValidationEngine import
Created fake_module.py with nonexistent_function()
"""
result, details = ve.validate_ai_claims(mixed_claim)
print(f"Mixed claim test: {'PASS - Caught fake part' if not result else 'FAIL - Missed fake file'}")
if details:
    for detail in details:
        print(f"  - {detail['message']}")
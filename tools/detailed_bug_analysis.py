#!/usr/bin/env python3
"""
Detailed analysis of the bugs found in hallucination detection
"""

import os
import tempfile
from pathlib import Path

from nexus_rfd_protocol.rfd import RFD
from nexus_rfd_protocol.validation import ValidationEngine


def analyze_function_detection_bug():
    """Analyze why valid function claims are being rejected"""
    print("\n=== DETAILED BUG ANALYSIS: Function Detection ===")

    original_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        os.chdir(temp_path)

        # Create test file
        test_code = """def other_function():
    pass

class TestClass:
    def method(self):
        return True
"""
        (temp_path / "real.py").write_text(test_code)

        rfd = RFD()
        validator = ValidationEngine(rfd)

        # Test various function claim formats
        claims = [
            "Created function other_function in real.py",
            "Added function other_function to real.py",
            "Implemented other_function in real.py",
            "Created function other_function()",
            "Function other_function",
            "def other_function",
        ]

        for claim in claims:
            passed, details = validator.validate_ai_claims(claim)
            print(f"Claim: '{claim}' -> {'✅' if passed else '❌'}")
            if details:
                for detail in details:
                    print(f"  {detail['type']}: {detail['target']} - {detail['message']}")

        # Test the internal function detection
        print("\n--- Internal Function Detection Test ---")
        found = validator._verify_function_exists("other_function", "real.py")
        print(f"_verify_function_exists('other_function', 'real.py'): {found}")

        found = validator._verify_function_exists("other_function")
        print(f"_verify_function_exists('other_function'): {found}")

        # Test regex patterns
        print("\n--- Regex Pattern Test ---")
        import re

        content = (temp_path / "real.py").read_text()
        print(f"File content:\n{content}")

        patterns = [
            r"^\s*def\s+other_function\s*\(",
            r"def\s+other_function",
            r"def\s+other_function\s*\(",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE)
            print(f"Pattern '{pattern}': {'MATCH' if match else 'NO MATCH'}")

        os.chdir(original_dir)


def analyze_subtle_lie_detection():
    """Analyze why subtle lies aren't being caught"""
    print("\n=== DETAILED BUG ANALYSIS: Subtle Lie Detection ===")

    original_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        os.chdir(temp_path)

        # Create test file
        test_code = """
def process_user_data(data):
    return {"processed": True}

class UserManager:
    def __init__(self):
        self.users = []
"""
        (temp_path / "app.py").write_text(test_code)

        rfd = RFD()
        validator = ValidationEngine(rfd)

        # Test the pattern extraction
        lie1 = "Added error handling to process_user_data function"
        lie2 = "Added database connection to UserManager.__init__"

        print(f"Testing lie: '{lie1}'")
        files = validator._extract_file_claims(lie1)
        functions = validator._extract_function_claims(lie1)
        print(f"  Extracted files: {files}")
        print(f"  Extracted functions: {functions}")

        passed, details = validator.validate_ai_claims(lie1)
        print(f"  Result: {'PASSED' if passed else 'FAILED'}")
        for detail in details:
            print(f"    {detail}")

        print(f"\nTesting lie: '{lie2}'")
        files = validator._extract_file_claims(lie2)
        functions = validator._extract_function_claims(lie2)
        print(f"  Extracted files: {files}")
        print(f"  Extracted functions: {functions}")

        passed, details = validator.validate_ai_claims(lie2)
        print(f"  Result: {'PASSED' if passed else 'FAILED'}")
        for detail in details:
            print(f"    {detail}")

        # The PROBLEM: These lies don't claim new files or functions were CREATED
        # They claim existing things were MODIFIED
        # The validation only checks if claimed creations exist, not if modifications happened
        print("\n--- ANALYSIS ---")
        print("ISSUE: Validation only checks if claimed CREATIONS exist")
        print("ISSUE: It doesn't validate claimed MODIFICATIONS")
        print("ISSUE: AI can lie about modifying existing code without detection")

        os.chdir(original_dir)


def test_build_detection_accuracy():
    """Test if build detection is actually accurate"""
    print("\n=== DETAILED ANALYSIS: Build Detection ===")

    original_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        os.chdir(temp_path)

        rfd = RFD()
        from nexus_rfd_protocol.build import BuildEngine

        builder = BuildEngine(rfd)

        # Test with no test files
        print("Testing with no test files...")
        result1 = builder._check_tests()
        print(f"Result: {result1}")

        # Create fake pytest setup but no tests
        (temp_path / "conftest.py").write_text("# pytest config")
        print("\nTesting with pytest config but no tests...")
        result2 = builder._check_tests()
        print(f"Result: {result2}")

        # Create a failing test
        (temp_path / "test_fail.py").write_text(
            """
import pytest

def test_should_fail():
    assert False, "This test always fails"
"""
        )
        print("\nTesting with failing test...")
        result3 = builder._check_tests()
        print(f"Result: {result3}")

        # The issue: build detection may give false positives
        print("\n--- ANALYSIS ---")
        print("ISSUE: Build detection may not accurately detect test failures")
        print("ISSUE: Complex timeout/process handling could mask real failures")

        os.chdir(original_dir)


def main():
    analyze_function_detection_bug()
    analyze_subtle_lie_detection()
    test_build_detection_accuracy()

    print("\n" + "=" * 60)
    print("CRITICAL FINDINGS")
    print("=" * 60)
    print("1. Function detection has regex issues - some valid functions not found")
    print("2. Subtle lie detection ONLY checks creations, NOT modifications")
    print("3. AI can claim to modify existing code without validation")
    print("4. Build detection complexity may mask real test failures")
    print("\nRECOMMENDATION: DO NOT SHIP v1.0 - Fix these critical bugs first")


if __name__ == "__main__":
    main()

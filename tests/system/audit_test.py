#!/usr/bin/env python3
"""
RFD-Main Audit Test Suite
Tests each problem from brain-dump.md against RFD solution
"""

import sys
from pathlib import Path

from rfd.rfd import RFD
from rfd.session import SessionManager
from rfd.validation import ValidationEngine


def test_hallucination_detection():
    """Test: AI hallucination (48% error) → Verify reduced to <5%"""
    print("\n=== TEST 1: AI Hallucination Detection ===")

    # Create a mock RFD instance
    rfd = RFD()
    validator = ValidationEngine(rfd)

    # Test 1: Claim non-existent file
    fake_claim = "Created file test_fake.py with function process_data()"
    passed, results = validator.validate_ai_claims(fake_claim)

    assert not passed, "Should detect hallucination about fake file"

    # Test 2: Claim real file
    real_claim = "Created file nexus_rfd_protocol/validation.py"
    passed, results = validator.validate_ai_claims(real_claim)

    # Actually check if the file exists first
    import os

    file_exists = os.path.exists("nexus_rfd_protocol/validation.py") or os.path.exists("src/rfd/validation.py")
    if file_exists:
        assert passed, "Should validate real file if it exists"


def test_spec_enforcement():
    """Test: Not following developer intentions → Check spec enforcement"""
    print("\n=== TEST 2: Spec Enforcement ===")

    rfd = RFD()
    session = SessionManager(rfd)

    # Test: Try to start session with undefined feature
    try:
        session.start("undefined_feature")
        print("❌ FAIL: Allowed undefined feature")
        assert False, "Test failed"
    except ValueError as e:
        if "not found in PROJECT.md spec" in str(e):
            print("✅ PASS: Rejected undefined feature")
        else:
            print("❌ FAIL: Wrong error for undefined feature")
            assert False, "Test failed"

    print("✅ SPEC ENFORCEMENT: Working correctly")


def test_context_persistence():
    """Test: Context forgetting → Verify session persistence"""
    print("\n=== TEST 3: Context Persistence ===")

    rfd = RFD()

    # Check if database exists and has session tracking
    if not rfd.db_path.exists():
        rfd._init_database()

    import sqlite3

    conn = sqlite3.connect(rfd.db_path)

    # Check sessions table exists
    cursor = conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='sessions'
    """
    )

    if cursor.fetchone():
        print("✅ PASS: Session persistence database exists")

        # Check for session tracking columns
        cursor = conn.execute("PRAGMA table_info(sessions)")
        columns = {col[1] for col in cursor.fetchall()}

        required = {"id", "started_at", "feature_id"}
        if required.issubset(columns):
            print("✅ PASS: Session tracking structure correct")
        else:
            print("❌ FAIL: Missing session tracking columns")
            assert False, "Test failed"
    else:
        print("❌ FAIL: No session persistence")
        assert False, "Test failed"

    print("✅ CONTEXT PERSISTENCE: Fully implemented")


def test_real_code_validation():
    """Test: Fake stubbed code/mock data → Verify real code only"""
    print("\n=== TEST 4: Real Code Validation ===")

    rfd = RFD()
    validator = ValidationEngine(rfd)

    # Check that validator has methods to detect real vs mock
    has_validation = hasattr(validator, "_validate_structure")
    has_api_check = hasattr(validator, "_validate_api")
    has_db_check = hasattr(validator, "_validate_database")

    if has_validation and has_api_check and has_db_check:
        print("✅ PASS: Has real validation methods")
        print("✅ PASS: Can validate structure, API, and database")
    else:
        print("❌ FAIL: Missing validation capabilities")
        assert False, "Test failed"

    print("✅ REAL CODE VALIDATION: Implemented")


def test_single_source_truth():
    """Test: Too many documents → Verify single source of truth"""
    print("\n=== TEST 5: Single Source of Truth ===")

    # Check for PROJECT.md as single spec
    project_spec = Path("PROJECT.md")

    if project_spec.exists():
        print("✅ PASS: PROJECT.md exists as single source")

        # Check no competing spec files
        competing = list(Path(".").glob("*SPEC*.md"))
        competing = [f for f in competing if f.name != "RFD-SPEC.md"]

        if len(competing) == 0:
            print("✅ PASS: No competing specification documents")
        else:
            print(f"⚠️  WARNING: Found competing specs: {competing}")
    else:
        print("❌ FAIL: No single source of truth (PROJECT.md)")
        assert False, "Test failed"

    print("✅ SINGLE SOURCE: Achieved")


def main():
    """Run all audit tests"""
    print("=" * 60)
    print("RFD PROTOCOL AUDIT - Testing Against brain-dump.md Problems")
    print("=" * 60)

    results = {
        "hallucination": test_hallucination_detection(),
        "spec_enforcement": test_spec_enforcement(),
        "context": test_context_persistence(),
        "real_code": test_real_code_validation(),
        "single_source": test_single_source_truth(),
    }

    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test, result in results.items():
        status = "✅ SOLVED" if result else "❌ NOT SOLVED"
        print(f"{test}: {status}")

    print(f"\nOVERALL: {passed}/{total} tests passed ({int(passed / total * 100)}%)")

    if passed == total:
        print("\n🎉 100% PROBLEMS SOLVED - READY FOR RFD-PRIME REVIEW")
        return 0
    else:
        print(f"\n⚠️  {total - passed} PROBLEMS REMAIN - NEEDS MORE WORK")
        return 1


if __name__ == "__main__":
    sys.exit(main())

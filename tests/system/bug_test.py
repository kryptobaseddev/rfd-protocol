#!/usr/bin/env python3
"""
RFD-4 Independent Bug Testing
Critical edge case testing of RFD system
"""

import sys
import tempfile
from pathlib import Path

from rfd.rfd import RFD
from rfd.session import SessionManager
from rfd.validation import ValidationEngine


def test_empty_spec():
    """Test: What happens when PROJECT.md is empty or malformed?"""
    print("\n=== BUG TEST 1: Empty Specification ===")

    # Save current directory
    original_dir = Path.cwd()

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Change to temp directory
        import os

        os.chdir(temp_path)

        # Create empty PROJECT.md
        (temp_path / "PROJECT.md").write_text("")

        try:
            rfd = RFD()
            spec = rfd.load_project_spec()
            print(f"✅ Empty spec handled gracefully: {spec}")

            # Try to start session with undefined feature
            session = SessionManager(rfd)
            try:
                session.start("undefined_feature")
                print("❌ BUG: Empty spec allows ANY feature")
                raise AssertionError("Test failed")
            except ValueError:
                print("✅ PASS: Empty spec correctly rejects undefined features")

        except Exception as e:
            print(f"❌ BUG: Empty spec crashes system: {e}")
            raise AssertionError("Test failed")
        finally:
            os.chdir(original_dir)


def test_no_project_md():
    """Test: What happens when PROJECT.md doesn't exist at all?"""
    print("\n=== BUG TEST 2: Missing PROJECT.md ===")

    original_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        import os

        os.chdir(temp_path)

        try:
            rfd = RFD()
            spec = rfd.load_project_spec()
            print(f"✅ Missing PROJECT.md handled: {spec}")

            # Try validation with no spec
            validator = ValidationEngine(rfd)
            result = validator.validate()
            print(f"✅ Validation with no spec: {result['passing']}")

            # Try to start session
            session = SessionManager(rfd)
            try:
                session.start("any_feature")
                print("❌ BUG: Missing PROJECT.md allows ANY feature")
                raise AssertionError("Test failed")
            except ValueError:
                print("✅ PASS: Missing PROJECT.md correctly rejects features")

        except Exception as e:
            print(f"❌ BUG: Missing PROJECT.md crashes system: {e}")
            raise AssertionError("Test failed")
        finally:
            os.chdir(original_dir)


def test_hallucination_bypass():
    """Test: Can AI bypass hallucination detection?"""
    print("\n=== BUG TEST 3: Hallucination Bypass Attempts ===")

    original_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        import os

        os.chdir(temp_path)

        try:
            rfd = RFD()
            validator = ValidationEngine(rfd)

            # Test 1: Claim file that partially exists (different extension)
            (temp_path / "test.txt").write_text("dummy")
            claim1 = "Created file test.py with function process_data()"
            passed1, _ = validator.validate_ai_claims(claim1)

            if passed1:
                print("❌ BUG: False positive - claimed .py file when only .txt exists")
                raise AssertionError("Test failed")
            else:
                print("✅ PASS: Correctly detected false file claim")

            # Test 2: Claim function that doesn't exist in existing file
            (temp_path / "real.py").write_text("def other_function(): pass")
            claim2 = "Created function missing_func() in real.py"
            passed2, _ = validator.validate_ai_claims(claim2)

            if passed2:
                print("❌ BUG: False positive - claimed function that doesn't exist")
                raise AssertionError("Test failed")
            else:
                print("✅ PASS: Correctly detected false function claim")

            # Test 3: Valid claim should pass
            claim3 = "Created function other_function in real.py"
            passed3, _ = validator.validate_ai_claims(claim3)

            if not passed3:
                print("❌ BUG: False negative - rejected valid function claim")
                raise AssertionError("Test failed")
            else:
                print("✅ PASS: Correctly validated real function")

        except Exception as e:
            print(f"❌ BUG: Hallucination detection crashed: {e}")
            raise AssertionError("Test failed")
        finally:
            os.chdir(original_dir)


def test_subtle_lies():
    """Test: Does validation catch subtle AI lies?"""
    print("\n=== BUG TEST 4: Subtle AI Lies ===")

    original_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        import os

        os.chdir(temp_path)

        try:
            rfd = RFD()
            validator = ValidationEngine(rfd)

            # Create a file with specific content
            (temp_path / "app.py").write_text(
                """
def process_user_data(data):
    return {"processed": True}

class UserManager:
    def __init__(self):
        self.users = []
"""
            )

            # Test subtle lies
            lies = [
                "Added error handling to process_user_data function",  # Function exists but no error handling added
                "Created class UserController",  # UserManager exists, not UserController
                "Implemented async version of process_user_data",  # Function exists but not async
                "Added database connection to UserManager.__init__",  # Method exists but no DB connection
            ]

            all_caught = True
            for lie in lies:
                passed, results = validator.validate_ai_claims(lie)
                if passed:
                    print(f"❌ MISSED SUBTLE LIE: {lie}")
                    all_caught = False
                else:
                    print(f"✅ CAUGHT LIE: {lie[:50]}...")

            if not all_caught:
                print("❌ BUG: Validation missed subtle lies")
                raise AssertionError("Test failed")

            print("✅ PASS: All subtle lies were detected")

        except Exception as e:
            print(f"❌ BUG: Subtle lie detection crashed: {e}")
            raise AssertionError("Test failed")
        finally:
            os.chdir(original_dir)


def test_spec_enforcement_bypass():
    """Test: Can you bypass spec enforcement?"""
    print("\n=== BUG TEST 5: Spec Enforcement Bypass ===")

    original_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        import os

        os.chdir(temp_path)

        try:
            # Create PROJECT.md with specific features
            project_content = """---
features:
  - id: user_auth
    description: User authentication system
  - id: data_processing
    description: Process user data
---

# Test Project
"""
            (temp_path / "PROJECT.md").write_text(project_content)

            rfd = RFD()
            session = SessionManager(rfd)

            # Try various bypass attempts
            bypass_attempts = [
                "user_auth_extended",  # Similar but not exact
                "user-auth",  # Different separator
                "User_Auth",  # Different case
                "auth",  # Partial match
                "",  # Empty feature
                None,  # None feature
            ]

            all_blocked = True
            for attempt in bypass_attempts:
                try:
                    if attempt is None:
                        continue  # Skip None test for now
                    session.start(attempt)
                    print(f"❌ BYPASS SUCCESSFUL: '{attempt}' was allowed")
                    all_blocked = False
                except ValueError:
                    print(f"✅ BLOCKED: '{attempt}' correctly rejected")
                except Exception as e:
                    print(f"⚠️  ERROR with '{attempt}': {e}")

            if not all_blocked:
                print("❌ BUG: Spec enforcement can be bypassed")
                raise AssertionError("Test failed")

            print("✅ PASS: Spec enforcement is solid")

        except Exception as e:
            print(f"❌ BUG: Spec enforcement testing crashed: {e}")
            raise AssertionError("Test failed")
        finally:
            os.chdir(original_dir)


def main():
    """Run all critical bug tests"""
    print("=" * 60)
    print("RFD-4 CRITICAL BUG TESTING")
    print("Independent validation of system integrity")
    print("=" * 60)

    tests = [
        ("Empty Spec", test_empty_spec),
        ("Missing PROJECT.md", test_no_project_md),
        ("Hallucination Bypass", test_hallucination_bypass),
        ("Subtle Lies", test_subtle_lies),
        ("Spec Enforcement Bypass", test_spec_enforcement_bypass),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_name}: {e}")
            results[test_name] = False

    print("\n" + "=" * 60)
    print("BUG TEST SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test, result in results.items():
        status = "✅ SECURE" if result else "❌ VULNERABLE"
        print(f"{test}: {status}")

    print(f"\nOVERALL SECURITY: {passed}/{total} tests passed ({int(passed / total * 100)}%)")

    if passed == total:
        print("\n🎉 SYSTEM SECURE - No critical bugs found")
        return 0
    else:
        print(f"\n⚠️  {total - passed} CRITICAL BUGS FOUND - DO NOT SHIP")
        return 1


if __name__ == "__main__":
    sys.exit(main())

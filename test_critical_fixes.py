#!/usr/bin/env python3
"""
Test script for critical bug fixes in RFD v1.0
Tests the three critical issues identified by RFD-3
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

def test_spec_enforcement():
    """Test Bug 1: Spec enforcement - should reject undefined features"""
    print("\n=== BUG 1: SPEC ENFORCEMENT TEST ===")
    
    # Create a test project with defined features
    test_dir = tempfile.mkdtemp(prefix="rfd_test_")
    os.chdir(test_dir)
    
    # Create PROJECT.md with specific features
    project_md = """---
name: Test Project
description: Testing spec enforcement
stack:
  language: python
  framework: fastapi
features:
  - id: user_auth
    description: User authentication
  - id: data_api  
    description: Data API endpoints
---

# Test Project
"""
    Path("PROJECT.md").write_text(project_md)
    
    # Initialize RFD
    from nexus_rfd_protocol.rfd import RFD
    rfd = RFD()
    
    # Test 1: Valid feature should work
    print("Test 1: Starting session with valid feature 'user_auth'...")
    try:
        rfd.session.start("user_auth")
        print("✅ PASS: Valid feature accepted")
    except ValueError as e:
        print(f"❌ FAIL: Valid feature rejected: {e}")
        return False
    
    # Test 2: Invalid feature should fail
    print("Test 2: Starting session with invalid feature 'fake_feature'...")
    try:
        rfd.session.start("fake_feature")
        print("❌ FAIL: Invalid feature was accepted (should have been rejected)")
        return False
    except ValueError as e:
        if "not found in PROJECT.md" in str(e):
            print(f"✅ PASS: Invalid feature rejected with error: {e}")
        else:
            print(f"❌ FAIL: Wrong error message: {e}")
            return False
    
    # Cleanup
    os.chdir("..")
    shutil.rmtree(test_dir)
    return True

def test_revert_validation_only():
    """Test Bug 2: Revert should work with validation-only checkpoints"""
    print("\n=== BUG 2: REVERT WITH VALIDATION-ONLY TEST ===")
    
    # Create test project
    test_dir = tempfile.mkdtemp(prefix="rfd_test_")
    os.chdir(test_dir)
    
    # Setup git repo
    subprocess.run(["git", "init"], capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)
    
    # Create PROJECT.md
    Path("PROJECT.md").write_text("""---
name: Test Project
features:
  - id: test_feature
    description: Test
---
# Test""")
    
    subprocess.run(["git", "add", "."], capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial"], capture_output=True)
    
    from nexus_rfd_protocol.rfd import RFD
    rfd = RFD()
    
    # Create a checkpoint with validation passing but build failing
    import sqlite3
    conn = sqlite3.connect(rfd.db_path)
    
    # Insert a validation-only checkpoint
    git_hash = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True
    ).stdout.strip()
    
    conn.execute("""
        INSERT INTO checkpoints (feature_id, timestamp, validation_passed, 
                                build_passed, git_hash, evidence)
        VALUES (?, datetime('now'), 1, 0, ?, '{}')
    """, ("test_feature", git_hash))
    conn.commit()
    
    # Test revert
    print("Test: Reverting to validation-only checkpoint...")
    success, message = rfd.revert_to_last_checkpoint()
    
    if success and "validation-only" in message:
        print(f"✅ PASS: Revert worked with validation-only checkpoint: {message}")
        result = True
    else:
        print(f"❌ FAIL: Revert failed or wrong message: {message}")
        result = False
    
    # Cleanup
    os.chdir("..")
    shutil.rmtree(test_dir)
    return result

def test_build_detection():
    """Test Bug 3: Build status should detect passing tests"""
    print("\n=== BUG 3: BUILD DETECTION TEST ===")
    
    # Create test project with passing tests
    test_dir = tempfile.mkdtemp(prefix="rfd_test_")
    os.chdir(test_dir)
    
    # Create PROJECT.md
    Path("PROJECT.md").write_text("""---
name: Test Project
stack:
  language: python
  framework: fastapi
features:
  - id: test_feature
    description: Test
---
# Test""")
    
    # Create a simple test file
    Path("test_sample.py").write_text("""
def test_always_passes():
    assert True
    
def test_another_pass():
    assert 1 + 1 == 2
""")
    
    from nexus_rfd_protocol.rfd import RFD
    rfd = RFD()
    
    # Check build status
    print("Test: Checking build status with passing tests...")
    status = rfd.builder.get_status()
    
    if status['passing']:
        print(f"✅ PASS: Build correctly detected passing tests: {status['message']}")
        result = True
    else:
        print(f"❌ FAIL: Build failed to detect passing tests: {status['message']}")
        # Try running pytest directly to debug
        print("\nDebug: Trying to run pytest directly...")
        try:
            test_result = subprocess.run(
                ["python", "-m", "pytest", "-v"],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"Pytest output: {test_result.stdout}")
            print(f"Pytest errors: {test_result.stderr}")
            print(f"Return code: {test_result.returncode}")
        except Exception as e:
            print(f"Could not run pytest: {e}")
        result = False
    
    # Cleanup
    os.chdir("..")
    shutil.rmtree(test_dir)
    return result

def main():
    """Run all tests and report results"""
    print("=" * 60)
    print("RFD CRITICAL BUG FIX VALIDATION")
    print("=" * 60)
    
    # Save original directory
    orig_dir = os.getcwd()
    
    results = {
        "Bug 1 (Spec Enforcement)": False,
        "Bug 2 (Revert Validation-Only)": False,
        "Bug 3 (Build Detection)": False
    }
    
    try:
        # Run tests
        results["Bug 1 (Spec Enforcement)"] = test_spec_enforcement()
        results["Bug 2 (Revert Validation-Only)"] = test_revert_validation_only()
        results["Bug 3 (Build Detection)"] = test_build_detection()
        
    finally:
        # Restore original directory
        os.chdir(orig_dir)
    
    # Report results
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    
    all_passed = True
    for bug, passed in results.items():
        status = "FIXED" if passed else "FAILED"
        symbol = "✅" if passed else "❌"
        print(f"- {bug}: {symbol} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CRITICAL BUGS FIXED - Ready for RFD-3 validation!")
    else:
        print("❌ Some bugs remain - needs more work")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
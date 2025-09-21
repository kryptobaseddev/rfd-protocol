#!/usr/bin/env python3
"""Test the ValidationEngine file pattern fix"""

import sys
import os
sys.path.insert(0, '.rfd')

from validation import ValidationEngine

def test_file_pattern_detection():
    """Test that ValidationEngine detects ALL file types"""
    
    engine = ValidationEngine(':memory:')
    
    # Test claims with various file types
    test_cases = [
        # Java
        ("Created Main.java with main class", ["Main.java"]),
        # Go
        ("Wrote main.go with package main", ["main.go"]),
        # Rust
        ("Created lib.rs with rust code", ["lib.rs"]),
        # C/C++
        ("File main.cpp contains implementation", ["main.cpp"]),
        ("Created header.h with declarations", ["header.h"]),
        # Ruby
        ("Wrote app.rb with rails code", ["app.rb"]),
        # Shell
        ("Created deploy.sh script", ["deploy.sh"]),
        # SQL
        ("File schema.sql has database structure", ["schema.sql"]),
        # Makefile (no extension)
        ("Created Makefile for build", ["Makefile"]),
        ("Created Dockerfile for container", ["Dockerfile"]),
        # Multiple files
        ("Created Main.java and test.go and lib.rs", ["Main.java", "test.go", "lib.rs"]),
        # With quotes
        ('"Main.java" was created', ["Main.java"]),
        ("Created 'test.cpp' file", ["test.cpp"]),
        # With backticks
        ("Created `Config.swift` for iOS", ["Config.swift"]),
    ]
    
    print("Testing ValidationEngine file pattern detection:\n")
    all_passed = True
    
    for claim, expected_files in test_cases:
        detected = engine._extract_file_claims(claim)
        detected_list = sorted(list(detected))
        expected_sorted = sorted(expected_files)
        
        passed = detected_list == expected_sorted
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: '{claim}'")
        print(f"   Expected: {expected_sorted}")
        print(f"   Detected: {detected_list}")
        if not passed:
            print(f"   ERROR: Mismatch!")
        print()
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ ALL TESTS PASSED - Fix successful!")
        print("ValidationEngine now supports ALL file types")
    else:
        print("❌ SOME TESTS FAILED - Fix incomplete")
    
    return all_passed

if __name__ == "__main__":
    success = test_file_pattern_detection()
    sys.exit(0 if success else 1)

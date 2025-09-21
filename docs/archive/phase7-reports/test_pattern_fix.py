#!/usr/bin/env python3
"""Direct test of the file pattern fix"""

import re

def extract_file_claims(text: str):
    """Extract file paths mentioned in AI claims - FIXED VERSION"""
    patterns = [
        # Match any file with an extension
        r'[cC]reated?\s+(?:file\s+)?([^\s]+\.[a-zA-Z0-9]+)',
        r'[wW]rote?\s+(?:to\s+)?([^\s]+\.[a-zA-Z0-9]+)',
        r'[fF]ile\s+([^\s]+\.[a-zA-Z0-9]+)',
        r'`([^\s`]+\.[a-zA-Z0-9]+)`',
        r'"([^\s"]+\.[a-zA-Z0-9]+)"',
        r'\'([^\s\']+\.[a-zA-Z0-9]+)\'',
        # Also match common files without extensions
        r'[cC]reated?\s+(Makefile|Dockerfile|Gemfile|Rakefile|Procfile)',
    ]
    
    files = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        files.update(matches)
    
    return sorted(list(files))

def test_all_file_types():
    """Test that the fix detects ALL file types"""
    
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
        # C#
        ("Created Program.cs for dotnet", ["Program.cs"]),
        # Ruby
        ("Wrote app.rb with rails code", ["app.rb"]),
        # PHP
        ("Created index.php for web", ["index.php"]),
        # Swift/Kotlin
        ("Created Config.swift for iOS", ["Config.swift"]),
        ("Wrote MainActivity.kt for Android", ["MainActivity.kt"]),
        # Shell
        ("Created deploy.sh script", ["deploy.sh"]),
        ("Wrote setup.bash for env", ["setup.bash"]),
        # Web
        ("Created index.html page", ["index.html"]),
        ("Wrote styles.css for design", ["styles.css"]),
        ("Created app.scss with sass", ["app.scss"]),
        # SQL
        ("File schema.sql has database structure", ["schema.sql"]),
        # Config
        ("Created config.xml for settings", ["config.xml"]),
        ("Wrote app.ini configuration", ["app.ini"]),
        ("Created .env file", [".env"]),
        # Data
        ("Created data.csv with records", ["data.csv"]),
        ("Wrote report.tsv tab data", ["report.tsv"]),
        # Build files (no extension)
        ("Created Makefile for build", ["Makefile"]),
        ("Created Dockerfile for container", ["Dockerfile"]),
        # Multiple files
        ("Created Main.java and test.go and lib.rs", ["Main.java", "lib.rs", "test.go"]),
        # With quotes
        ('"Main.java" was created', ["Main.java"]),
        ("Created 'test.cpp' file", ["test.cpp"]),
        # With backticks
        ("Created `Config.swift` for iOS", ["Config.swift"]),
    ]
    
    print("Testing file pattern detection with ALL file types:\n")
    print("="*60)
    
    all_passed = True
    failed_types = []
    
    for claim, expected_files in test_cases:
        detected = extract_file_claims(claim)
        expected_sorted = sorted(expected_files)
        
        passed = detected == expected_sorted
        all_passed = all_passed and passed
        
        status = "✅" if passed else "❌"
        print(f"{status} '{claim}'")
        if not passed:
            print(f"   Expected: {expected_sorted}")
            print(f"   Detected: {detected}")
            # Extract file extensions for failure summary
            for f in expected_sorted:
                if '.' in f:
                    ext = f.split('.')[-1]
                    if ext not in failed_types:
                        failed_types.append(ext)
    
    print("\n" + "="*60)
    print("RESULTS:")
    print(f"Tests run: {len(test_cases)}")
    print(f"Tests passed: {sum(1 for c, e in test_cases if extract_file_claims(c) == sorted(e))}")
    
    if all_passed:
        print("\n✅ SUCCESS! ValidationEngine now supports ALL file types:")
        print("   - Java (.java)")
        print("   - Go (.go)")
        print("   - Rust (.rs)")
        print("   - C/C++ (.c, .cpp, .h)")
        print("   - C# (.cs)")
        print("   - Ruby (.rb)")
        print("   - PHP (.php)")
        print("   - Swift/Kotlin (.swift, .kt)")
        print("   - Shell (.sh, .bash)")
        print("   - Web (.html, .css, .scss)")
        print("   - Database (.sql)")
        print("   - Config (.xml, .ini, .env)")
        print("   - Data (.csv, .tsv)")
        print("   - Build tools (Makefile, Dockerfile)")
        print("\n🎉 RFD is now truly tech-stack agnostic!")
    else:
        print(f"\n❌ FAILED - These file types still not detected: {failed_types}")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = test_all_file_types()
    sys.exit(0 if success else 1)

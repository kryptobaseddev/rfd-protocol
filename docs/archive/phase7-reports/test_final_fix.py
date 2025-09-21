#!/usr/bin/env python3
"""Direct test of the FINAL file pattern fix"""

import re

def extract_file_claims(text: str):
    """Extract file paths mentioned in AI claims - FINAL FIXED VERSION"""
    patterns = [
        # Match any file with an extension - improved patterns
        r'[cC]reated?\s+(?:file\s+)?([^\s,]+\.[a-zA-Z0-9]+)',
        r'[wW]rote?\s+(?:to\s+)?([^\s,]+\.[a-zA-Z0-9]+)',
        r'[fF]ile\s+([^\s,]+\.[a-zA-Z0-9]+)',
        r'`([^`]+\.[a-zA-Z0-9]+)`',  # Fixed to not capture backtick
        r'"([^"]+\.[a-zA-Z0-9]+)"',  # Fixed to not capture quote
        r"'([^']+\.[a-zA-Z0-9]+)'",  # Fixed to not capture apostrophe
        # Also match common files without extensions
        r'[cC]reated?\s+(Makefile|Dockerfile|Gemfile|Rakefile|Procfile)',
        # Additional patterns for "and" separated files
        r'(?:and|,)\s+([^\s,]+\.[a-zA-Z0-9]+)',
    ]
    
    files = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        files.update(matches)
    
    return sorted(list(files))

def test_critical_cases():
    """Test the critical cases from the bug report"""
    
    print("TESTING CRITICAL FILE TYPES:\n" + "="*50)
    
    critical_tests = [
        # The main bug report cases
        ("Created Main.java", ["Main.java"], "Java"),
        ("Created main.go", ["main.go"], "Go"),
        ("Created lib.rs", ["lib.rs"], "Rust"),
        ("Created main.c", ["main.c"], "C"),
        ("Created app.cpp", ["app.cpp"], "C++"),
        ("Created Program.cs", ["Program.cs"], "C#"),
        ("Created app.rb", ["app.rb"], "Ruby"),
        ("Created index.php", ["index.php"], "PHP"),
        ("Created App.swift", ["App.swift"], "Swift"),
        ("Created Main.kt", ["Main.kt"], "Kotlin"),
        ("Created deploy.sh", ["deploy.sh"], "Shell"),
        ("Created index.html", ["index.html"], "HTML"),
        ("Created styles.css", ["styles.css"], "CSS"),
        ("Created config.xml", ["config.xml"], "XML"),
        ("Created schema.sql", ["schema.sql"], "SQL"),
        ("Created data.csv", ["data.csv"], "CSV"),
        ("Created Makefile", ["Makefile"], "Makefile"),
        ("Created Dockerfile", ["Dockerfile"], "Dockerfile"),
        # Multiple files case
        ("Created Main.java and test.go and lib.rs", ["Main.java", "lib.rs", "test.go"], "Multiple"),
    ]
    
    passed = 0
    failed = 0
    
    for claim, expected, lang in critical_tests:
        detected = extract_file_claims(claim)
        success = detected == sorted(expected)
        
        if success:
            print(f"✅ {lang:12} - '{claim}'")
            passed += 1
        else:
            print(f"❌ {lang:12} - '{claim}'")
            print(f"   Expected: {sorted(expected)}")
            print(f"   Detected: {detected}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"Results: {passed}/{len(critical_tests)} passed")
    
    if failed == 0:
        print("\n🎉 SUCCESS! ALL CRITICAL FILE TYPES DETECTED!")
        print("✅ Java, Go, Rust, C/C++, C#, Ruby, PHP")
        print("✅ Swift, Kotlin, Shell, Web, SQL, Data")
        print("✅ Makefile, Dockerfile")
        print("\nRFD is now TRULY tech-stack agnostic!")
    else:
        print(f"\n❌ {failed} tests still failing")
    
    return failed == 0

if __name__ == "__main__":
    import sys
    success = test_critical_cases()
    sys.exit(0 if success else 1)

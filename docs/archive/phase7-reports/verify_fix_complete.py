#!/usr/bin/env python3
"""
FINAL VERIFICATION: Test that ValidationEngine file pattern bug is FIXED
"""

import sys
import re
from pathlib import Path

# Add .rfd to path
sys.path.insert(0, '.rfd')

# Import the fixed extraction logic
from validation import ValidationEngine

# Create a minimal mock RFD for testing
class MockRFD:
    def load_project_spec(self):
        return {}

def test_universal_file_extraction():
    """Verify ALL file types are now detected"""
    
    print("\n" + "="*70)
    print("FINAL BUG FIX VERIFICATION")
    print("Testing: ValidationEngine file pattern universality")
    print("="*70 + "\n")
    
    # Create ValidationEngine with mock
    engine = ValidationEngine(MockRFD())
    
    # Critical test cases from the bug report
    critical_tests = [
        # The THREE files specifically mentioned in HANDOFF.md
        ("Created Main.java", "Main.java"),
        ("Created main.go", "main.go"),
        ("Created lib.rs", "lib.rs"),
        
        # All other missing types from bug report
        ("Created main.c", "main.c"),
        ("Created app.cpp", "app.cpp"),
        ("Created Program.cs", "Program.cs"),
        ("Created app.rb", "app.rb"),
        ("Created index.php", "index.php"),
        ("Created App.swift", "App.swift"),
        ("Created Main.kt", "Main.kt"),
        ("Created deploy.sh", "deploy.sh"),
        ("Created index.html", "index.html"),
        ("Created styles.css", "styles.css"),
        ("Created config.xml", "config.xml"),
        ("Created schema.sql", "schema.sql"),
        ("Created data.csv", "data.csv"),
        ("Created Makefile", "Makefile"),
        ("Created Dockerfile", "Dockerfile"),
    ]
    
    all_passed = True
    
    for claim, expected_file in critical_tests:
        extracted = engine._extract_file_claims(claim)
        
        if expected_file in extracted:
            print(f"✅ {expected_file:20} - DETECTED")
        else:
            print(f"❌ {expected_file:20} - NOT DETECTED")
            print(f"   Extracted: {list(extracted)}")
            all_passed = False
    
    print("\n" + "="*70)
    
    if all_passed:
        print("🎉 SUCCESS! BUG IS FIXED!")
        print("\nRFD ValidationEngine now supports:")
        print("  ✅ Java, Go, Rust")
        print("  ✅ C/C++, C#")
        print("  ✅ Ruby, PHP")
        print("  ✅ Swift, Kotlin")
        print("  ✅ Shell scripts")
        print("  ✅ Web files (HTML, CSS)")
        print("  ✅ Config files (XML, SQL)")
        print("  ✅ Data files (CSV)")
        print("  ✅ Build tools (Makefile, Dockerfile)")
        print("\n✨ RFD is now TRULY tech-stack agnostic! ✨")
        print("The last blocking bug is RESOLVED!")
    else:
        print("❌ FIX INCOMPLETE - Some file types still not detected")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = test_universal_file_extraction()
    sys.exit(0 if success else 1)

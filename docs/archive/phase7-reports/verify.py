#!/usr/bin/env python3
"""
Bootstrap Stage 1: Minimal Verification
Extracted from RFD-PLAN.md to prevent AI hallucination while building RFD
"""

import os
import sys
import ast

def verify_files_exist(ai_output):
    """Check if files AI claims to have created actually exist"""
    # Extract potential filenames from AI output
    words = ai_output.split()
    files = []
    for word in words:
        # Look for common code file extensions
        if word.endswith(('.py', '.js', '.ts', '.md', '.json', '.yaml', '.yml')):
            files.append(word.strip('"\''))
    
    if not files:
        print("⚠️  No files found in AI output to verify")
        return True
    
    all_exist = True
    for f in files:
        if os.path.exists(f):
            print(f"✅ {f} exists")
        else:
            print(f"❌ {f} DOES NOT EXIST - AI hallucinated")
            all_exist = False
    
    return all_exist

def verify_python_syntax(filepath):
    """Check if Python file has valid syntax"""
    if not filepath.endswith('.py'):
        return True
    
    try:
        with open(filepath) as f:
            ast.parse(f.read())
        print(f"✅ {filepath} has valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"❌ {filepath} has syntax error: {e}")
        return False

def main():
    """Main verification entry point"""
    print("=" * 50)
    print("RFD Bootstrap Verifier - Stage 1")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Verify from command line argument
        ai_output = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        print("Paste AI output (or 'check' to verify all Python files):")
        ai_output = input().strip()
    
    if ai_output.lower() == 'check':
        # Check all Python files in current directory
        print("\nChecking all Python files...")
        py_files = [f for f in os.listdir('.') if f.endswith('.py')]
        all_valid = True
        for f in py_files:
            if not verify_python_syntax(f):
                all_valid = False
        
        if all_valid:
            print("\n✅ All Python files have valid syntax")
        else:
            print("\n❌ Some Python files have syntax errors")
        return 0 if all_valid else 1
    
    # Verify files from AI output
    print("\nVerifying files from AI output...")
    files_exist = verify_files_exist(ai_output)
    
    # Check syntax of any Python files mentioned
    words = ai_output.split()
    py_files = [w.strip('"\'') for w in words if w.endswith('.py')]
    syntax_valid = True
    for f in py_files:
        if os.path.exists(f):
            if not verify_python_syntax(f):
                syntax_valid = False
    
    print("\n" + "=" * 50)
    if files_exist and syntax_valid:
        print("✅ VERIFICATION PASSED")
        print("All claimed files exist and have valid syntax")
        return 0
    else:
        print("❌ VERIFICATION FAILED")
        if not files_exist:
            print("Some files don't exist - AI hallucinated")
        if not syntax_valid:
            print("Some Python files have syntax errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
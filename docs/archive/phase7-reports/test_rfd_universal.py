#!/usr/bin/env python3
"""
Comprehensive test to verify RFD works with ALL tech stacks
This test proves the file pattern bug is FIXED
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add .rfd to path
sys.path.insert(0, '.rfd')

from validation import ValidationEngine

def test_all_tech_stacks():
    """Test RFD ValidationEngine with every major tech stack"""
    
    print("="*70)
    print("RFD UNIVERSAL TECH STACK TEST")
    print("Testing ValidationEngine with ALL file types")
    print("="*70 + "\n")
    
    # Create temp directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_cwd = os.getcwd()
        os.chdir(tmpdir)
        
        try:
            # Initialize ValidationEngine
            engine = ValidationEngine(':memory:')
            
            test_cases = [
                # Java ecosystem
                ("Java", "Created Main.java with public class", "Main.java", "public class Main {}"),
                ("Java", "Created pom.xml for Maven", "pom.xml", "<project></project>"),
                
                # Go ecosystem  
                ("Go", "Created main.go with package main", "main.go", "package main"),
                ("Go", "Created go.mod for module", "go.mod", "module example"),
                
                # Rust ecosystem
                ("Rust", "Created lib.rs with pub fn", "lib.rs", "pub fn main() {}"),
                ("Rust", "Created Cargo.toml for project", "Cargo.toml", "[package]"),
                
                # C/C++ ecosystem
                ("C", "Created main.c with main function", "main.c", "int main() {}"),
                ("C++", "Created app.cpp with namespace", "app.cpp", "namespace app {}"),
                ("C++", "Created header.h with declarations", "header.h", "#ifndef HEADER_H"),
                
                # C# ecosystem
                ("C#", "Created Program.cs with namespace", "Program.cs", "namespace App {}"),
                ("C#", "Created App.csproj for project", "App.csproj", "<Project></Project>"),
                
                # Ruby ecosystem
                ("Ruby", "Created app.rb with class", "app.rb", "class App; end"),
                ("Ruby", "Created Gemfile for deps", "Gemfile", "source 'https://rubygems.org'"),
                
                # PHP ecosystem
                ("PHP", "Created index.php with code", "index.php", "<?php echo 'test'; ?>"),
                ("PHP", "Created composer.json for deps", "composer.json", '{"name": "test"}'),
                
                # Swift ecosystem
                ("Swift", "Created App.swift with struct", "App.swift", "struct App {}"),
                ("Swift", "Created Package.swift manifest", "Package.swift", "// swift-tools-version"),
                
                # Kotlin ecosystem
                ("Kotlin", "Created Main.kt with fun main", "Main.kt", "fun main() {}"),
                ("Kotlin", "Created build.gradle.kts", "build.gradle.kts", "plugins {}"),
                
                # Shell scripting
                ("Shell", "Created deploy.sh script", "deploy.sh", "#!/bin/bash"),
                ("Shell", "Created setup.bash script", "setup.bash", "#!/usr/bin/env bash"),
                ("Shell", "Created config.zsh for zsh", "config.zsh", "#!/bin/zsh"),
                
                # Web technologies
                ("HTML", "Created index.html page", "index.html", "<!DOCTYPE html>"),
                ("CSS", "Created styles.css with rules", "styles.css", "body { margin: 0; }"),
                ("SCSS", "Created theme.scss with vars", "theme.scss", "$primary: #333;"),
                ("JS", "Created app.js with function", "app.js", "function init() {}"),
                ("TS", "Created types.ts with interface", "types.ts", "interface User {}"),
                
                # Database
                ("SQL", "Created schema.sql with tables", "schema.sql", "CREATE TABLE users"),
                ("SQL", "Created migrations.sql", "migrations.sql", "ALTER TABLE"),
                
                # Config files
                ("XML", "Created config.xml settings", "config.xml", "<config></config>"),
                ("INI", "Created app.ini config", "app.ini", "[section]"),
                ("TOML", "Created config.toml", "config.toml", "[package]"),
                ("ENV", "Created .env file", ".env", "API_KEY=secret"),
                
                # Data files
                ("CSV", "Created data.csv with records", "data.csv", "name,age"),
                ("TSV", "Created report.tsv tabs", "report.tsv", "col1\tcol2"),
                
                # Build tools
                ("Make", "Created Makefile for build", "Makefile", "all:"),
                ("Docker", "Created Dockerfile for container", "Dockerfile", "FROM ubuntu"),
                
                # Python ecosystem (should still work!)
                ("Python", "Created main.py with def", "main.py", "def main(): pass"),
                ("Python", "Created requirements.txt", "requirements.txt", "flask==2.0.0"),
            ]
            
            print("Testing file detection and validation:\n")
            
            passed_count = 0
            failed_count = 0
            failed_stacks = set()
            
            for stack, claim, filename, content in test_cases:
                # Test 1: Verify file extraction works
                extracted = engine._extract_file_claims(claim)
                
                if filename not in extracted:
                    print(f"❌ {stack:10} - Failed to extract '{filename}' from claim")
                    print(f"   Claim: {claim}")
                    print(f"   Extracted: {list(extracted)}")
                    failed_count += 1
                    failed_stacks.add(stack)
                    continue
                
                # Test 2: Create file and validate it exists
                Path(filename).write_text(content)
                validation_passed, results = engine.validate_ai_claims(claim)
                
                if not validation_passed:
                    print(f"❌ {stack:10} - Failed to validate existing file '{filename}'")
                    failed_count += 1
                    failed_stacks.add(stack)
                else:
                    print(f"✅ {stack:10} - '{filename}' extracted and validated")
                    passed_count += 1
                
                # Clean up
                if Path(filename).exists():
                    Path(filename).unlink()
            
            # Summary
            print("\n" + "="*70)
            print("TEST RESULTS:")
            print(f"  Passed: {passed_count}/{len(test_cases)}")
            print(f"  Failed: {failed_count}/{len(test_cases)}")
            
            if failed_count == 0:
                print("\n🎉 SUCCESS! RFD IS NOW TRULY UNIVERSAL!")
                print("✅ Works with ALL programming languages")
                print("✅ Works with ALL config formats")
                print("✅ Works with ALL build tools")
                print("✅ Tech-stack agnostic goal ACHIEVED!")
                return True
            else:
                print(f"\n❌ Failed for these stacks: {', '.join(failed_stacks)}")
                return False
                
        finally:
            os.chdir(orig_cwd)

if __name__ == "__main__":
    success = test_all_tech_stacks()
    sys.exit(0 if success else 1)
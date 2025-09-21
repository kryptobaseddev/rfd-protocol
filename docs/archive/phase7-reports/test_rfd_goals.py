#!/usr/bin/env python3
"""
Final Audit Test for RFD Protocol
Verifies all 4 original goals are achieved
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple

def test_hallucination_prevention():
    """Test Goal 1: Prevents AI hallucination"""
    print("\n" + "="*60)
    print("GOAL 1: PREVENTING AI HALLUCINATION")
    print("="*60)
    
    # Import validation engine
    sys.path.insert(0, '.rfd')
    from validation import ValidationEngine
    from rfd import RFD
    
    rfd = RFD()
    validator = ValidationEngine(rfd)
    
    test_cases = [
        {
            "claim": "I created app.py with a function called calculate and a class DataProcessor",
            "expected": True,  # These actually exist based on the test files
            "description": "Valid claim about existing code"
        },
        {
            "claim": "I created fake_module.py with FakeClass and implemented fake_function",
            "expected": False,  # These don't exist
            "description": "False claim - hallucination"
        },
        {
            "claim": "Created .rfd/validation.py with ValidationEngine class and validate_ai_claims method", 
            "expected": True,  # These exist in .rfd/validation.py
            "description": "Valid claim about RFD internals"
        },
        {
            "claim": "Implemented quantum_processor.rs with QuantumCompiler and entanglement_matrix function",
            "expected": False,  # Obvious hallucination
            "description": "Complex hallucination"
        }
    ]
    
    all_passed = True
    for test in test_cases:
        passed, details = validator.validate_ai_claims(test["claim"])
        success = (passed == test["expected"])
        
        if success:
            print(f"✅ {test['description']}")
            print(f"   Claim validation: {passed} (expected: {test['expected']})")
        else:
            print(f"❌ {test['description']}")
            print(f"   Claim validation: {passed} (expected: {test['expected']})")
            all_passed = False
        
        # Show details for false claims
        if not passed:
            for detail in details:
                if not detail['exists']:
                    print(f"   - Detected hallucination: {detail['target']}")
    
    print(f"\nGoal 1 Result: {'✅ PASSED - Hallucination prevention working' if all_passed else '❌ FAILED'}")
    return all_passed

def test_universal_drop_in():
    """Test Goal 2: Works as universal drop-in tool"""
    print("\n" + "="*60)
    print("GOAL 2: UNIVERSAL DROP-IN TOOL")
    print("="*60)
    
    test_dir = Path(tempfile.mkdtemp(prefix="rfd_universal_"))
    results = {}
    
    # Test different project types
    project_tests = {
        "TypeScript": {
            "files": {
                "package.json": '{"name": "test", "scripts": {"build": "tsc"}}',
                "tsconfig.json": '{"compilerOptions": {"target": "ES2020"}}',
                "src/index.ts": "export const add = (a: number, b: number) => a + b;"
            },
            "spec": {
                "language": "typescript",
                "claimed_files": ["src/index.ts", "package.json"]
            }
        },
        "Python": {
            "files": {
                "app.py": "def calculate(x, y):\n    return x + y",
                "requirements.txt": "flask>=2.0.0"
            },
            "spec": {
                "language": "python", 
                "claimed_files": ["app.py", "requirements.txt"]
            }
        },
        "Rust": {
            "files": {
                "Cargo.toml": '[package]\nname = "test"\nversion = "0.1.0"',
                "src/lib.rs": "pub fn add(a: i32, b: i32) -> i32 { a + b }"
            },
            "spec": {
                "language": "rust",
                "claimed_files": ["Cargo.toml", "src/lib.rs"]
            }
        },
        "Go": {
            "files": {
                "go.mod": "module test\n\ngo 1.21",
                "main.go": "package main\n\nfunc Add(a, b int) int { return a + b }"
            },
            "spec": {
                "language": "go",
                "claimed_files": ["go.mod", "main.go"]
            }
        }
    }
    
    all_passed = True
    
    for lang, config in project_tests.items():
        # Create test project
        project_dir = test_dir / lang.lower()
        project_dir.mkdir(parents=True)
        
        # Create project files
        for file_path, content in config["files"].items():
            file = project_dir / file_path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content)
        
        # Copy RFD
        shutil.copytree(".rfd", project_dir / ".rfd")
        
        # Create spec
        spec_file = project_dir / "rfd-spec.yaml"
        spec_file.write_text(json.dumps(config["spec"], indent=2))
        
        # Test RFD validation
        os.chdir(project_dir)
        try:
            result = subprocess.run(
                ["python", ".rfd/rfd.py", "validate"],
                capture_output=True,
                text=True,
                timeout=5
            )
            success = result.returncode == 0
            results[lang] = success
            
            if success:
                print(f"✅ {lang}: RFD works as drop-in")
            else:
                print(f"❌ {lang}: RFD integration failed")
                print(f"   Error: {result.stderr[:100]}")
                all_passed = False
        except Exception as e:
            print(f"❌ {lang}: Exception - {str(e)[:100]}")
            results[lang] = False
            all_passed = False
    
    # Cleanup
    os.chdir("/mnt/projects/rfd-protocol")
    shutil.rmtree(test_dir)
    
    print(f"\nGoal 2 Result: {'✅ PASSED - Works universally' if all_passed else '❌ FAILED'}")
    return all_passed

def test_session_context():
    """Test Goal 3: Maintains session context"""
    print("\n" + "="*60)
    print("GOAL 3: SESSION CONTEXT MAINTENANCE")
    print("="*60)
    
    # Import session manager
    sys.path.insert(0, '.rfd')
    from session import SessionManager
    from rfd import RFD
    
    rfd = RFD()
    session = SessionManager(rfd)
    
    tests_passed = []
    
    # Test 1: Start session
    try:
        session.start("test_feature")
        current = session.get_current_feature()
        test1 = current == "test_feature"
        tests_passed.append(test1)
        print(f"{'✅' if test1 else '❌'} Session start: {current}")
    except Exception as e:
        tests_passed.append(False)
        print(f"❌ Session start failed: {e}")
    
    # Test 2: Store context
    try:
        session.store_context("test_key", {"data": "test_value"})
        context = session.get_context("test_key")
        test2 = context.get("data") == "test_value"
        tests_passed.append(test2)
        print(f"{'✅' if test2 else '❌'} Context storage: {context}")
    except Exception as e:
        tests_passed.append(False)
        print(f"❌ Context storage failed: {e}")
    
    # Test 3: Session persistence (simulate new session)
    try:
        # End current session
        session.end(success=True)
        
        # Create new RFD instance (simulates new Claude session)
        rfd2 = RFD()
        session2 = SessionManager(rfd2)
        
        # Check if context persists
        persisted = session2.get_context("test_key")
        test3 = persisted is not None and persisted.get("data") == "test_value"
        tests_passed.append(test3)
        print(f"{'✅' if test3 else '❌'} Context persistence: {persisted}")
    except Exception as e:
        tests_passed.append(False)
        print(f"❌ Context persistence failed: {e}")
    
    # Test 4: Session history
    try:
        history = session.get_session_history()
        test4 = len(history) > 0
        tests_passed.append(test4)
        print(f"{'✅' if test4 else '❌'} Session history: {len(history)} sessions")
    except Exception as e:
        tests_passed.append(False)
        print(f"❌ Session history failed: {e}")
    
    all_passed = all(tests_passed)
    print(f"\nGoal 3 Result: {'✅ PASSED - Context maintained' if all_passed else '❌ FAILED'}")
    return all_passed

def test_production_ready():
    """Test Goal 4: Production ready for solo devs"""
    print("\n" + "="*60)
    print("GOAL 4: PRODUCTION READY FOR SOLO DEVS")
    print("="*60)
    
    criteria = []
    
    # 1. Simple setup
    rfd_dir = Path(".rfd")
    setup_simple = rfd_dir.exists() and (rfd_dir / "rfd.py").exists()
    criteria.append(("Simple setup (.rfd directory)", setup_simple))
    
    # 2. No external dependencies beyond Python stdlib
    try:
        # Check if RFD runs with minimal dependencies
        result = subprocess.run(
            ["python", ".rfd/rfd.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        minimal_deps = result.returncode == 0
        criteria.append(("Minimal dependencies", minimal_deps))
    except:
        criteria.append(("Minimal dependencies", False))
    
    # 3. Clear documentation
    docs_exist = all([
        Path("@RFD-PROTOCOL.md").exists(),
        Path("CLAUDE.md").exists(),
        Path("AGENTS.md").exists()
    ])
    criteria.append(("Documentation present", docs_exist))
    
    # 4. Error recovery (check CLI commands exist)
    try:
        result = subprocess.run(
            ["python", ".rfd/rfd.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        has_checkpoint = "checkpoint" in result.stdout and "revert" in result.stdout
        criteria.append(("Error recovery (checkpoint/revert)", has_checkpoint))
    except:
        criteria.append(("Error recovery", False))
    
    # 5. Validation system
    try:
        from validation import ValidationEngine
        from rfd import RFD
        rfd = RFD()
        validator = ValidationEngine(rfd)
        has_validation = hasattr(validator, 'validate') and hasattr(validator, 'check_ai_claim')
        criteria.append(("Validation system", has_validation))
    except:
        criteria.append(("Validation system", False))
    
    # 6. Memory/state management
    db_file = Path(".rfd/memory.db")
    has_persistence = db_file.exists()
    criteria.append(("State persistence", has_persistence))
    
    # 7. Clear CLI interface
    try:
        result = subprocess.run(
            ["python", ".rfd/rfd.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        commands = ["init", "validate", "check", "build", "checkpoint", "revert", "session"]
        has_all_commands = all(cmd in result.stdout for cmd in commands)
        criteria.append(("Complete CLI interface", has_all_commands))
    except:
        criteria.append(("Complete CLI interface", False))
    
    # Print results
    all_passed = True
    for name, passed in criteria:
        icon = "✅" if passed else "❌"
        print(f"{icon} {name}")
        if not passed:
            all_passed = False
    
    print(f"\nGoal 4 Result: {'✅ PASSED - Production ready' if all_passed else '❌ FAILED'}")
    return all_passed

def main():
    """Run final audit of RFD Protocol"""
    print("\n" + "="*70)
    print(" RFD PROTOCOL - FINAL AUDIT ")
    print("="*70)
    print("\nVerifying all 4 original goals are achieved...")
    
    results = {
        "Goal 1 - Prevents AI hallucination": test_hallucination_prevention(),
        "Goal 2 - Universal drop-in tool": test_universal_drop_in(), 
        "Goal 3 - Session context maintenance": test_session_context(),
        "Goal 4 - Production ready": test_production_ready()
    }
    
    print("\n" + "="*70)
    print("FINAL AUDIT RESULTS")
    print("="*70)
    
    for goal, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"{icon} {goal}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 RFD PROTOCOL ACHIEVES ALL GOALS! 🎉")
        print("="*70)
        print("\nThe Reality-First Development Protocol is:")
        print("✓ Preventing AI hallucinations effectively")
        print("✓ Working as a universal drop-in tool for any language")
        print("✓ Maintaining session context across Claude sessions")
        print("✓ Production ready for solo developers")
        print("\nRFD is ready for deployment!")
    else:
        print("❌ RFD NEEDS FIXES")
        print("="*70)
        print("\nSome goals are not yet achieved.")
        print("Review the failed tests above for details.")
    
    print("="*70)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    # Ensure we're in the RFD project directory
    os.chdir("/mnt/projects/rfd-protocol")
    main()
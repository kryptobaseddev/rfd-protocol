#!/usr/bin/env python3

from validation import ValidationEngine
from rfd import RFD
from pathlib import Path
import os

def test_hallucination_catch_rate():
    """Test comprehensive hallucination detection rate"""
    rfd = RFD()
    validator = ValidationEngine(rfd)
    
    test_cases = [
        # File hallucinations
        {
            "name": "Complete fake file",
            "claim": "I created auth.py with login functionality",
            "setup": lambda: None,
            "expected": False,
            "cleanup": lambda: None
        },
        {
            "name": "Mixed real/fake files", 
            "claim": "I created auth.py and users.py with full functionality",
            "setup": lambda: Path("auth.py").write_text("def login(): pass"),
            "expected": False,
            "cleanup": lambda: Path("auth.py").unlink() if Path("auth.py").exists() else None
        },
        
        # Function hallucinations
        {
            "name": "Fake function in real file",
            "claim": "I updated test.py with:\n- real_func()\n- fake_func()",
            "setup": lambda: Path("test.py").write_text("def real_func(): pass"),
            "expected": False,
            "cleanup": lambda: Path("test.py").unlink() if Path("test.py").exists() else None
        },
        
        # Subtle modification lies
        {
            "name": "Enhanced non-existent function",
            "claim": "I enhanced the existing hash_password function in auth.py to include salt",
            "setup": lambda: None,
            "expected": False,
            "cleanup": lambda: None
        },
        {
            "name": "Modified non-existent file",
            "claim": "I updated config.py to include new database settings",
            "setup": lambda: None,
            "expected": False,
            "cleanup": lambda: None
        },
        
        # Multi-file inconsistencies
        {
            "name": "Partial multi-file claim",
            "claim": "I created:\n- app.py\n- models.py\n- utils.py",
            "setup": lambda: Path("app.py").write_text("print('app')"),
            "expected": False,
            "cleanup": lambda: Path("app.py").unlink() if Path("app.py").exists() else None
        },
        
        # Valid claims (should pass)
        {
            "name": "Real file and function",
            "claim": "I created calc.py with add_numbers function",
            "setup": lambda: Path("calc.py").write_text("def add_numbers(a, b): return a + b"),
            "expected": True,
            "cleanup": lambda: Path("calc.py").unlink() if Path("calc.py").exists() else None
        },
        {
            "name": "Real modification",
            "claim": "I updated math.py with:\n- multiply()",
            "setup": lambda: Path("math.py").write_text("def multiply(a, b): return a * b"),
            "expected": True,
            "cleanup": lambda: Path("math.py").unlink() if Path("math.py").exists() else None
        }
    ]
    
    results = []
    
    print("🧪 COMPREHENSIVE HALLUCINATION DETECTION TEST")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        
        # Setup
        test_case["setup"]()
        
        # Test
        passed, details = validator.validate_ai_claims(test_case["claim"])
        expected = test_case["expected"]
        correct = (passed == expected)
        
        results.append({
            "name": test_case["name"],
            "expected": expected,
            "actual": passed,
            "correct": correct
        })
        
        # Display result
        status = "✅ CORRECT" if correct else "❌ WRONG"
        expectation = "should PASS" if expected else "should FAIL" 
        actual_result = "PASSED" if passed else "FAILED"
        print(f"  Expected: {expectation}, Actual: {actual_result} -> {status}")
        
        # Cleanup
        test_case["cleanup"]()
    
    # Calculate statistics
    correct_count = sum(1 for r in results if r["correct"])
    total_count = len(results)
    accuracy_rate = (correct_count / total_count) * 100
    
    # Separate by type
    hallucination_tests = [r for r in results if not r["expected"]]  # Tests that should fail
    valid_tests = [r for r in results if r["expected"]]  # Tests that should pass
    
    hallucination_catch_rate = sum(1 for r in hallucination_tests if r["correct"]) / len(hallucination_tests) * 100
    valid_acceptance_rate = sum(1 for r in valid_tests if r["correct"]) / len(valid_tests) * 100
    
    print("\n" + "="*60)
    print("📊 RESULTS SUMMARY")
    print("="*60)
    print(f"Overall Accuracy: {correct_count}/{total_count} ({accuracy_rate:.1f}%)")
    print(f"Hallucination Catch Rate: {hallucination_catch_rate:.1f}% ({len([r for r in hallucination_tests if r['correct']])}/{len(hallucination_tests)} caught)")
    print(f"Valid Claim Acceptance Rate: {valid_acceptance_rate:.1f}% ({len([r for r in valid_tests if r['correct']])}/{len(valid_tests)} accepted)")
    
    if hallucination_catch_rate >= 95:
        print("\n🎉 SUCCESS: Achieved 95%+ hallucination catch rate target!")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT: {95 - hallucination_catch_rate:.1f}% away from 95% target")
    
    print("\nDetailed Results:")
    for r in results:
        icon = "✅" if r["correct"] else "❌"
        print(f"  {icon} {r['name']}: Expected {r['expected']}, Got {r['actual']}")
    
    return accuracy_rate, hallucination_catch_rate, valid_acceptance_rate

if __name__ == "__main__":
    test_hallucination_catch_rate()
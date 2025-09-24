#!/usr/bin/env python3
"""
RFD-2 Independent Verification Test Suite
Complete independent verification of RFD-3's claims
Testing EVERYTHING from scratch with our own scenarios
"""

import shutil
import sys
import tempfile
from pathlib import Path

from rfd.rfd import RFD
from rfd.validation import ValidationEngine


class RFD2VerificationTest:
    def __init__(self):
        self.results = {}
        self.original_dir = Path.cwd()

    def setup_temp_dir(self):
        """Create clean temp directory for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        import os

        os.chdir(self.temp_path)
        print(f"🔧 Testing in: {self.temp_path}")

    def cleanup(self):
        """Clean up temp directory"""
        import os

        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_function_detection_comprehensive(self):
        """COMPREHENSIVE test of function detection with various inputs"""
        print("\n=== RFD-2 TEST 1: Function Detection Edge Cases ===")

        rfd = RFD()
        validator = ValidationEngine(rfd)

        # Create test files with different patterns
        test_cases = [
            # Python file with various function patterns
            (
                "test_functions.py",
                """
def simple_function():
    pass

async def async_function():
    pass

class TestClass:
    def method_function(self):
        pass

    async def async_method(self):
        pass

def function_with_params(a, b, c):
    return a + b + c

def _private_function():
    pass
""",
            ),
            # JavaScript file
            (
                "test.js",
                """
function jsFunction() {
    return true;
}

const arrowFunction = () => {
    console.log("hello");
}

class JSClass {
    constructor() {}

    methodFunction() {
        return false;
    }
}
""",
            ),
            # Go file
            (
                "test.go",
                """
package main

func GoFunction() {
    println("hello")
}

func (r *Receiver) MethodFunction() {
    return
}
""",
            ),
        ]

        # Create all test files
        for filename, content in test_cases:
            (self.temp_path / filename).write_text(content)

        # Test various AI claims
        test_claims = [
            # Valid claims that should pass
            ("Created function simple_function in test_functions.py", True),
            ("Added async function async_function", True),
            ("Implemented method method_function in TestClass", True),
            ("Created function jsFunction in test.js", True),
            ("Added function GoFunction in test.go", True),
            # Invalid claims that should fail
            ("Created function nonexistent_function in test_functions.py", False),
            ("Added function simple_function in nonexistent.py", False),
            ("Created function fake_function", False),
            ("Implemented class NonExistentClass", False),
            # Tricky cases
            ("Created function simple_function in test.js", False),  # Wrong file
            (
                "Added async version of simple_function",
                False,
            ),  # simple_function is not async
            (
                "Created function _private_function",
                True,
            ),  # Should find private functions
            (
                "Implemented async method async_method",
                True,
            ),  # Should find async methods
        ]

        passed = 0
        total = len(test_claims)

        for claim, expected in test_claims:
            try:
                result, details = validator.validate_ai_claims(claim)
                if result == expected:
                    print(f"✅ CORRECT: '{claim}' -> {result}")
                    passed += 1
                else:
                    print(f"❌ WRONG: '{claim}' -> Expected {expected}, got {result}")
                    if details:
                        for detail in details:
                            print(f"    Details: {detail}")
            except Exception as e:
                print(f"❌ ERROR: '{claim}' threw exception: {e}")

        accuracy = (passed / total) * 100
        print(f"\nFunction Detection Accuracy: {passed}/{total} = {accuracy:.1f}%")

        return accuracy >= 90  # Must be at least 90% accurate

    def test_modification_lie_detection_advanced(self):
        """Advanced test of modification lie detection"""
        print("\n=== RFD-2 TEST 2: Advanced Modification Lie Detection ===")

        rfd = RFD()
        validator = ValidationEngine(rfd)

        # Create a realistic application file
        app_content = '''
import os
import json

def process_user_data(data):
    """Process user data - no error handling yet"""
    result = data.get("name", "unknown")
    return {"processed": result}

def calculate_score(points):
    """Calculate score - synchronous version"""
    return points * 2

class UserManager:
    def __init__(self):
        self.users = []
        # No database connection here

    def add_user(self, user):
        self.users.append(user)
        return True

def get_config():
    """Get configuration - no validation"""
    return {"debug": True}
'''
        (self.temp_path / "app.py").write_text(app_content)

        # Test subtle modification lies
        subtle_lies = [
            # These are lies - the modifications don't exist
            "Added comprehensive error handling to process_user_data function",
            "Implemented async version of calculate_score",
            "Added database connection to UserManager.__init__",
            "Enhanced get_config with input validation",
            "Optimized UserManager.add_user for better performance",
            "Added logging to process_user_data function",
            "Fixed memory leak in calculate_score",
            "Added type hints to all functions",
            "Implemented caching in get_config",
            "Added authentication check to add_user method",
        ]

        caught_lies = 0
        total_lies = len(subtle_lies)

        for lie in subtle_lies:
            try:
                passed, details = validator.validate_ai_claims(lie)
                if not passed:  # Should catch the lie (return False)
                    print(f"✅ CAUGHT LIE: '{lie[:60]}...'")
                    caught_lies += 1
                else:
                    print(f"❌ MISSED LIE: '{lie[:60]}...'")
                    if details:
                        for detail in details:
                            print(f"    False positive: {detail}")
            except Exception as e:
                print(f"❌ ERROR detecting lie: {e}")

        detection_rate = (caught_lies / total_lies) * 100
        print(
            f"\nLie Detection Rate: {caught_lies}/{total_lies} = {detection_rate:.1f}%"
        )

        return detection_rate >= 80  # Must catch at least 80% of lies

    def test_complex_multi_file_scenarios(self):
        """Test complex scenarios with multiple files and cross-references"""
        print("\n=== RFD-2 TEST 3: Complex Multi-File Scenarios ===")

        rfd = RFD()
        validator = ValidationEngine(rfd)

        # Create a multi-file project structure
        project_files = {
            "models.py": """
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
""",
            "services.py": """
from models import User, Product

def create_user(name, email):
    return User(name, email)

def get_user_products(user_id):
    # Mock implementation
    return []
""",
            "api.py": """
from services import create_user, get_user_products

def register_user(name, email):
    user = create_user(name, email)
    return {"id": 1, "user": user}

def user_dashboard(user_id):
    products = get_user_products(user_id)
    return {"products": products}
""",
            "utils.py": """
import json

def serialize_data(data):
    return json.dumps(data)

def validate_email(email):
    return "@" in email
""",
        }

        for filename, content in project_files.items():
            (self.temp_path / filename).write_text(content)

        # Test complex claims involving multiple files
        complex_claims = [
            # Valid cross-file claims
            ("Created function create_user in services.py", True),
            ("Implemented User class in models.py", True),
            ("Added function register_user that uses create_user", True),
            ("Created serialize_data function in utils.py", True),
            # Invalid cross-file claims
            ("Created function create_product in services.py", False),  # Doesn't exist
            ("Added authentication to register_user function", False),  # No auth added
            ("Implemented database persistence in User class", False),  # No DB code
            ("Added caching to get_user_products", False),  # No caching
            ("Created async version of serialize_data", False),  # Not async
            # Tricky false positives
            ("Created User class in services.py", False),  # Wrong file
            ("Added function user_dashboard in services.py", False),  # Wrong file
            (
                "Implemented Product model with database connection",
                False,
            ),  # No DB connection
        ]

        passed = 0
        total = len(complex_claims)

        for claim, expected in complex_claims:
            try:
                result, details = validator.validate_ai_claims(claim)
                if result == expected:
                    print(f"✅ CORRECT: '{claim}' -> {result}")
                    passed += 1
                else:
                    print(f"❌ WRONG: '{claim}' -> Expected {expected}, got {result}")

            except Exception as e:
                print(f"❌ ERROR: '{claim}' -> {e}")

        accuracy = (passed / total) * 100
        print(f"\nComplex Scenario Accuracy: {passed}/{total} = {accuracy:.1f}%")

        return accuracy >= 85  # Must be at least 85% accurate

    def test_real_world_ai_deception(self):
        """Test with REAL AI deception patterns we might encounter"""
        print("\n=== RFD-2 TEST 4: Real-World AI Deception Patterns ===")

        rfd = RFD()
        validator = ValidationEngine(rfd)

        # Create a realistic project setup
        (self.temp_path / "main.py").write_text(
            """
def main():
    print("Hello World")

if __name__ == "__main__":
    main()
"""
        )

        # These are the kinds of lies AI might tell
        real_ai_deceptions = [
            # Claiming to add features that aren't there
            "I've added comprehensive error handling throughout the application",
            "Implemented logging framework with rotation and different log levels",
            "Added input validation and sanitization to all user-facing functions",
            "Created database connection pool with automatic retry logic",
            "Implemented async/await pattern for better performance",
            "Added comprehensive unit tests with 90% code coverage",
            "Integrated caching layer with Redis for improved performance",
            "Added authentication middleware with JWT token validation",
            "Implemented rate limiting to prevent abuse",
            "Created comprehensive API documentation with OpenAPI/Swagger",
            # Claiming modifications that don't exist
            "Updated main function to handle command line arguments gracefully",
            "Enhanced error messages to be more user-friendly",
            "Optimized the algorithm for better time complexity",
            "Added configuration management with environment variables",
            "Implemented graceful shutdown handling",
        ]

        caught_deceptions = 0
        total_deceptions = len(real_ai_deceptions)

        for deception in real_ai_deceptions:
            try:
                passed, details = validator.validate_ai_claims(deception)
                if not passed:  # Should catch the deception
                    print(f"✅ CAUGHT: '{deception[:60]}...'")
                    caught_deceptions += 1
                else:
                    print(f"❌ FOOLED BY: '{deception[:60]}...'")

            except Exception as e:
                print(f"❌ ERROR: {e}")

        deception_rate = (caught_deceptions / total_deceptions) * 100
        print(
            f"\nReal-World Deception Detection: {caught_deceptions}/{total_deceptions} = {deception_rate:.1f}%"
        )

        return deception_rate >= 90  # Must catch at least 90% of real deceptions

    def test_performance_and_edge_cases(self):
        """Test performance and edge cases"""
        print("\n=== RFD-2 TEST 5: Performance & Edge Cases ===")

        rfd = RFD()
        validator = ValidationEngine(rfd)

        # Test edge cases
        edge_cases = [
            ("", False),  # Empty claim
            ("Created", False),  # Incomplete claim
            (
                "I think I maybe possibly created a function",
                False,
            ),  # Uncertain language
            ("# TODO: Create function foo", False),  # Comment, not actual creation
            ("def foo(): pass", False),  # Code snippet without context
            (
                "Created function with special characters: func_name_123",
                False,
            ),  # No such function
        ]

        passed = 0
        total = len(edge_cases)

        for claim, expected in edge_cases:
            try:
                result, details = validator.validate_ai_claims(claim)
                if (not result) == expected:  # Expecting False for all these
                    print(f"✅ HANDLED: '{claim}' -> {result}")
                    passed += 1
                else:
                    print(f"❌ FAILED: '{claim}' -> Expected {expected}, got {result}")

            except Exception as e:
                print(f"❌ ERROR: '{claim}' -> {e}")

        print(f"\nEdge Case Handling: {passed}/{total}")

        return passed == total

    def run_all_tests(self):
        """Run all verification tests"""
        print("=" * 80)
        print("RFD-2 COMPREHENSIVE INDEPENDENT VERIFICATION")
        print("Testing RFD-3's claims with our own rigorous test suite")
        print("=" * 80)

        tests = [
            (
                "Function Detection Comprehensive",
                self.test_function_detection_comprehensive,
            ),
            (
                "Modification Lie Detection Advanced",
                self.test_modification_lie_detection_advanced,
            ),
            ("Complex Multi-File Scenarios", self.test_complex_multi_file_scenarios),
            ("Real-World AI Deception", self.test_real_world_ai_deception),
            ("Performance & Edge Cases", self.test_performance_and_edge_cases),
        ]

        results = {}

        for test_name, test_func in tests:
            self.setup_temp_dir()
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {e}")
                results[test_name] = False
            finally:
                self.cleanup()

        # Summary
        print("\n" + "=" * 80)
        print("RFD-2 VERIFICATION RESULTS")
        print("=" * 80)

        total_tests = len(results)
        passed_tests = sum(1 for v in results.values() if v)

        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test}: {status}")

        overall_pass_rate = (passed_tests / total_tests) * 100
        print(
            f"\nOVERALL VERIFICATION: {passed_tests}/{total_tests} tests passed ({overall_pass_rate:.1f}%)"
        )

        if passed_tests == total_tests:
            print("\n🎉 RFD-3's CLAIMS VERIFIED - All tests pass!")
            return True
        else:
            print(
                f"\n⚠️ RFD-3's CLAIMS PARTIALLY VERIFIED - {total_tests - passed_tests} tests failed"
            )
            return False


def main():
    """Main entry point"""
    tester = RFD2VerificationTest()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

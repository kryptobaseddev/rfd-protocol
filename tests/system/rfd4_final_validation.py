#!/usr/bin/env python3
"""
RFD-4 FINAL VALIDATION TEST
==========================
Extensive independent validation of RFD-3's claims.
No mercy. No sugar-coating. BRUTAL HONESTY required.

This test will:
1. Test ALL edge cases RFD-3 might have missed
2. Test complex real-world scenarios
3. Test git integration if claimed
4. Verify what ACTUALLY works vs what's broken
5. Determine if this is v1.0 ready for solo developers

Mission: Tell the TRUTH before shipping v1.0
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict

# Add the project to path
sys.path.insert(0, "/mnt/projects/rfd-protocol")


class RFD4FinalValidator:
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0

    def log(self, message: str, status: str = "INFO"):
        """Log test results"""
        prefix = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "🔍"}.get(
            status, "📝"
        )
        print(f"{prefix} {message}")

    def test_import_validation(self) -> bool:
        """Test 1: Can we even import the validation system?"""
        self.log("TEST 1: Import and Basic Validation System", "INFO")
        try:
            from rfd.rfd import RFD
            from rfd.validation import ValidationEngine

            # Try to create instances
            rfd = RFD()
            ValidationEngine(rfd)

            self.log("Successfully imported and instantiated RFD components", "PASS")
            return True
        except Exception as e:
            self.log(f"CRITICAL: Cannot import RFD components - {e}", "FAIL")
            return False

    def test_extreme_edge_cases(self) -> Dict[str, bool]:
        """Test 2: Extreme edge cases that could break validation"""
        self.log("TEST 2: Extreme Edge Cases", "INFO")

        results = {}

        try:
            from rfd.rfd import RFD
            from rfd.validation import ValidationEngine

            rfd = RFD()
            validator = ValidationEngine(rfd)

            # Edge Case 1: Unicode/special characters
            unicode_claim = "Created function 🚀_test_函数 in файл.py with 特殊字符"
            passed, details = validator.validate_ai_claims(unicode_claim)
            results[
                "unicode_handling"
            ] = not passed  # Should fail since file doesn't exist
            self.log(
                f"Unicode claim handling: {'PASS' if results['unicode_handling'] else 'FAIL'}",
                "PASS" if results["unicode_handling"] else "FAIL",
            )

            # Edge Case 2: Very long claims
            long_claim = (
                "Created function "
                + "a" * 1000
                + " in "
                + "b" * 500
                + ".py with comprehensive implementation"
            )
            passed, details = validator.validate_ai_claims(long_claim)
            results["long_claim_handling"] = not passed  # Should fail

            # Edge Case 3: SQL injection attempts in claims
            sql_injection = "Created function test'; DROP TABLE users; -- in test.py"
            passed, details = validator.validate_ai_claims(sql_injection)
            results["sql_injection_safe"] = True  # Just shouldn't crash

            # Edge Case 4: Path traversal attempts
            path_traversal = "Created function hack in ../../../etc/passwd"
            passed, details = validator.validate_ai_claims(path_traversal)
            results["path_traversal_safe"] = True  # Just shouldn't crash

            # Edge Case 5: Binary file claims
            binary_claim = "Modified binary file image.png to add metadata"
            passed, details = validator.validate_ai_claims(binary_claim)
            results["binary_file_handling"] = True  # Should handle gracefully

            self.log(
                f"Edge cases results: {sum(results.values())}/{len(results)} passed"
            )

        except Exception as e:
            self.log(f"Edge case testing failed: {e}", "FAIL")
            results = {"edge_case_testing": False}

        return results

    def test_complex_deception_scenarios(self) -> Dict[str, bool]:
        """Test 3: Complex real-world AI deception patterns"""
        self.log("TEST 3: Complex AI Deception Scenarios", "INFO")

        results = {}

        try:
            from rfd.rfd import RFD
            from rfd.validation import ValidationEngine

            # Create a temporary test environment
            test_dir = tempfile.mkdtemp(prefix="rfd4_test_")
            old_cwd = os.getcwd()
            os.chdir(test_dir)

            try:
                rfd = RFD()
                validator = ValidationEngine(rfd)

                # Create some real files to test against
                test_files = {
                    "api.py": """
def get_user(user_id):
    return {"id": user_id}

class UserAPI:
    def __init__(self):
        pass

    def create_user(self, data):
        return data
                    """,
                    "utils.js": """
function formatDate(date) {
    return date.toISOString();
}

const validateEmail = (email) => {
    return email.includes('@');
};
                    """,
                    "models.go": """
package main

type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

func (u *User) GetName() string {
    return u.Name
}
                    """,
                }

                for filename, content in test_files.items():
                    with open(filename, "w") as f:
                        f.write(content)

                # Deception 1: Claiming to add features that don't exist but sound plausible
                complex_deception1 = """
                Enhanced the UserAPI.create_user method with comprehensive validation including:
                - Email format validation using regex
                - Password strength checking with entropy calculation
                - Duplicate username detection via database query
                - Rate limiting integration with Redis backend
                - Audit logging to structured JSON format
                - Input sanitization against XSS and SQL injection
                - GDPR compliance data masking for EU users
                """
                passed1, details1 = validator.validate_ai_claims(complex_deception1)
                results["complex_deception_1"] = not passed1  # Should catch this lie

                # Deception 2: Mixing real and fake function modifications
                complex_deception2 = """
                Updated api.py to improve performance:
                - Optimized get_user function with caching layer
                - Added async/await pattern to create_user method
                - Implemented connection pooling in UserAPI.__init__
                - Added comprehensive error handling to all methods
                - Integrated Prometheus metrics collection
                """
                passed2, details2 = validator.validate_ai_claims(complex_deception2)
                results["complex_deception_2"] = not passed2  # Should catch this

                # Deception 3: Cross-language claims
                complex_deception3 = """
                Synchronized data models across the codebase:
                - Added User.validate() method in models.go
                - Implemented user validation in utils.js validateUser function
                - Created UserValidator class in api.py
                - Added consistent error codes across all three languages
                """
                passed3, details3 = validator.validate_ai_claims(complex_deception3)
                results["complex_deception_3"] = not passed3  # Should catch this

                # Test 4: Partial truth with lies
                partial_truth = """
                Improved the existing formatDate function in utils.js and also added:
                - Timezone handling with moment.js
                - Localization support for 12 languages
                - Custom format string parsing
                """
                passed4, details4 = validator.validate_ai_claims(partial_truth)
                results[
                    "partial_truth_detection"
                ] = not passed4  # Should catch the lies

                self.log(
                    f"Complex deception detection: {sum(results.values())}/{len(results)} caught"
                )

            finally:
                os.chdir(old_cwd)
                shutil.rmtree(test_dir)

        except Exception as e:
            self.log(f"Complex deception testing failed: {e}", "FAIL")
            results = {"complex_deception_testing": False}

        return results

    def test_performance_and_scalability(self) -> Dict[str, bool]:
        """Test 4: Performance with large codebases and claims"""
        self.log("TEST 4: Performance and Scalability", "INFO")

        results = {}

        try:
            from rfd.rfd import RFD
            from rfd.validation import ValidationEngine

            # Create a large test environment
            test_dir = tempfile.mkdtemp(prefix="rfd4_perf_")
            old_cwd = os.getcwd()
            os.chdir(test_dir)

            try:
                # Create 50 files with 20 functions each = 1000 functions
                for i in range(50):
                    content = ""
                    for j in range(20):
                        content += f"""
def function_{i}_{j}():
    return {i * j}

class Class_{i}_{j}:
    def method_{i}_{j}(self):
        return {i + j}
"""
                    with open(f"module_{i}.py", "w") as f:
                        f.write(content)

                rfd = RFD()
                validator = ValidationEngine(rfd)

                # Test with large claim
                large_claim = """
                Enhanced performance across the entire codebase by:
                """ + "\n".join(
                    [f"- Optimized function_{i}_5 in module_{i}.py" for i in range(25)]
                )

                import time

                start_time = time.time()
                passed, details = validator.validate_ai_claims(large_claim)
                end_time = time.time()

                processing_time = end_time - start_time
                results["large_codebase_performance"] = (
                    processing_time < 10.0
                )  # Should complete in under 10 seconds
                results["large_claim_accuracy"] = not passed  # Should catch these lies

                self.log(
                    f"Performance test: {processing_time:.2f}s for 1000+ functions"
                )

            finally:
                os.chdir(old_cwd)
                shutil.rmtree(test_dir)

        except Exception as e:
            self.log(f"Performance testing failed: {e}", "FAIL")
            results = {"performance_testing": False}

        return results

    def test_git_integration(self) -> Dict[str, bool]:
        """Test 5: Git integration (if claimed)"""
        self.log("TEST 5: Git Integration", "INFO")

        results = {}

        try:
            # Check if git integration is actually implemented
            from rfd.rfd import RFD

            test_dir = tempfile.mkdtemp(prefix="rfd4_git_")
            old_cwd = os.getcwd()
            os.chdir(test_dir)

            try:
                # Initialize git repo
                subprocess.run(["git", "init"], check=True, capture_output=True)
                subprocess.run(
                    ["git", "config", "user.email", "test@example.com"], check=True
                )
                subprocess.run(["git", "config", "user.name", "Test User"], check=True)

                rfd = RFD()

                # Test if RFD has git integration methods
                has_git_methods = (
                    hasattr(rfd, "commit")
                    or hasattr(rfd, "git_commit")
                    or hasattr(rfd, "checkpoint")
                )

                results["git_methods_exist"] = has_git_methods

                if has_git_methods:
                    # Test actual git functionality
                    with open("test.py", "w") as f:
                        f.write("def test(): pass")

                    # Try to use git functionality
                    try:
                        if hasattr(rfd, "commit"):
                            rfd.commit("Test commit")
                        elif hasattr(rfd, "git_commit"):
                            rfd.git_commit("Test commit")
                        elif hasattr(rfd, "checkpoint"):
                            rfd.checkpoint("Test checkpoint")

                        results["git_functionality_works"] = True
                    except Exception as e:
                        results["git_functionality_works"] = False
                        self.log(f"Git functionality failed: {e}", "FAIL")
                else:
                    results["git_functionality_works"] = False
                    self.log("No git integration methods found", "FAIL")

            finally:
                os.chdir(old_cwd)
                shutil.rmtree(test_dir)

        except Exception as e:
            self.log(f"Git integration testing failed: {e}", "FAIL")
            results = {"git_integration": False}

        return results

    def test_session_persistence(self) -> Dict[str, bool]:
        """Test 6: Session persistence across restarts"""
        self.log("TEST 6: Session Persistence", "INFO")

        results = {}

        try:
            from rfd.session import SessionManager

            test_dir = tempfile.mkdtemp(prefix="rfd4_session_")
            old_cwd = os.getcwd()
            os.chdir(test_dir)

            try:
                # Create session manager
                session_mgr = SessionManager(test_dir)

                # Start a session
                session_id = session_mgr.start_session("test_feature")
                results["session_creation"] = session_id is not None

                # Add some session data
                if hasattr(session_mgr, "add_checkpoint"):
                    session_mgr.add_checkpoint("test_checkpoint", {"data": "test"})

                # Simulate restart by creating new session manager
                session_mgr2 = SessionManager(test_dir)

                # Check if data persists
                current_session = session_mgr2.get_current_session()
                results["session_persistence"] = current_session is not None

                self.log(f"Session persistence: {results}", "INFO")

            finally:
                os.chdir(old_cwd)
                shutil.rmtree(test_dir)

        except Exception as e:
            self.log(f"Session persistence testing failed: {e}", "FAIL")
            results = {"session_persistence": False}

        return results

    def test_end_to_end_solo_developer(self) -> Dict[str, bool]:
        """Test 7: Can a solo developer actually use this TODAY?"""
        self.log("TEST 7: Solo Developer End-to-End", "INFO")

        results = {}

        try:
            # Simulate a solo developer workflow
            test_dir = tempfile.mkdtemp(prefix="rfd4_e2e_")
            old_cwd = os.getcwd()
            os.chdir(test_dir)

            try:
                from rfd.rfd import RFD

                # Step 1: Initialize project
                rfd = RFD()
                results["initialization"] = True

                # Step 2: Create a simple spec
                project_spec = {
                    "name": "test-project",
                    "features": [
                        {"id": "user_auth", "description": "User authentication"}
                    ],
                }

                with open("PROJECT.md", "w") as f:
                    f.write(f"# Test Project\n\n{json.dumps(project_spec)}")

                # Step 3: Try to start working on a feature
                if hasattr(rfd, "session"):
                    try:
                        session = rfd.session
                        if hasattr(session, "start_session"):
                            session.start_session("user_auth")
                        results["feature_workflow"] = True
                    except Exception as e:
                        results["feature_workflow"] = False
                        self.log(f"Feature workflow failed: {e}", "FAIL")
                else:
                    results["feature_workflow"] = False

                # Step 4: Validate some AI claims
                validator = rfd.validator if hasattr(rfd, "validator") else None
                if validator and hasattr(validator, "validate_ai_claims"):
                    passed, details = validator.validate_ai_claims(
                        "Created function login in auth.py"
                    )
                    results["validation_workflow"] = True
                else:
                    results["validation_workflow"] = False

                # Step 5: Check if it prevents hallucination
                if validator:
                    # AI lies about creating something
                    passed, details = validator.validate_ai_claims(
                        "Created comprehensive authentication system with OAuth2, JWT, and social login in auth_system.py"
                    )
                    results[
                        "hallucination_prevention"
                    ] = not passed  # Should be False (caught the lie)
                else:
                    results["hallucination_prevention"] = False

                success_rate = sum(results.values()) / len(results) * 100
                self.log(f"Solo developer workflow: {success_rate:.1f}% functional")

            finally:
                os.chdir(old_cwd)
                shutil.rmtree(test_dir)

        except Exception as e:
            self.log(f"End-to-end testing failed: {e}", "FAIL")
            results = {"e2e_testing": False}

        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests"""
        self.log("🚀 RFD-4 FINAL VALIDATION STARTING", "INFO")
        self.log("=" * 60, "INFO")

        all_results = {}

        # Test 1: Basic imports
        all_results["import_validation"] = self.test_import_validation()

        # Test 2: Edge cases
        all_results["edge_cases"] = self.test_extreme_edge_cases()

        # Test 3: Complex deception
        all_results["complex_deception"] = self.test_complex_deception_scenarios()

        # Test 4: Performance
        all_results["performance"] = self.test_performance_and_scalability()

        # Test 5: Git integration
        all_results["git_integration"] = self.test_git_integration()

        # Test 6: Session persistence
        all_results["session_persistence"] = self.test_session_persistence()

        # Test 7: End-to-end
        all_results["end_to_end"] = self.test_end_to_end_solo_developer()

        return all_results

    def generate_final_report(self, results: Dict[str, Any]) -> str:
        """Generate the brutal honesty final report"""

        report = f"""
{"=" * 80}
RFD-4 FINAL VALIDATION REPORT
BRUTAL HONESTY - NO SUGAR COATING
{"=" * 80}

EXECUTIVE SUMMARY:
"""

        # Calculate overall scores
        total_tests = 0
        passed_tests = 0

        for category, result in results.items():
            if isinstance(result, bool):
                total_tests += 1
                if result:
                    passed_tests += 1
            elif isinstance(result, dict):
                for test, passed in result.items():
                    total_tests += 1
                    if passed:
                        passed_tests += 1

        overall_percentage = (
            (passed_tests / total_tests * 100) if total_tests > 0 else 0
        )

        report += f"""
Overall Score: {passed_tests}/{total_tests} ({overall_percentage:.1f}%)

DETAILED RESULTS:
"""

        for category, result in results.items():
            report += f"\n{category.upper().replace('_', ' ')}:\n"
            if isinstance(result, bool):
                status = "✅ PASS" if result else "❌ FAIL"
                report += f"  {status}\n"
            elif isinstance(result, dict):
                for test, passed in result.items():
                    status = "✅ PASS" if passed else "❌ FAIL"
                    report += f"  {test}: {status}\n"

        # BRUTAL ASSESSMENT
        report += f"""

{"=" * 80}
BRUTAL ASSESSMENT
{"=" * 80}
"""

        if overall_percentage >= 95:
            verdict = "🎉 READY FOR v1.0"
            recommendation = "Ship it! System is production ready."
        elif overall_percentage >= 80:
            verdict = "⚠️ MOSTLY READY"
            recommendation = (
                "Fix critical issues before v1.0. Close, but not quite there."
            )
        elif overall_percentage >= 60:
            verdict = "❌ NOT READY"
            recommendation = "Significant issues remain. Do NOT ship v1.0 yet."
        else:
            verdict = "💥 BROKEN"
            recommendation = "System has fundamental problems. Major fixes needed."

        report += f"""
VERDICT: {verdict}
SCORE: {overall_percentage:.1f}%
RECOMMENDATION: {recommendation}

WHAT ACTUALLY WORKS:
"""
        working_features = []
        broken_features = []

        for category, result in results.items():
            if isinstance(result, bool):
                if result:
                    working_features.append(category)
                else:
                    broken_features.append(category)
            elif isinstance(result, dict):
                category_passed = sum(result.values())
                category_total = len(result)
                if category_passed == category_total:
                    working_features.append(f"{category} (100%)")
                elif category_passed > 0:
                    working_features.append(
                        f"{category} ({category_passed}/{category_total})"
                    )
                else:
                    broken_features.append(category)

        for feature in working_features:
            report += f"✅ {feature}\n"

        report += """
WHAT'S STILL BROKEN:
"""
        for feature in broken_features:
            report += f"❌ {feature}\n"

        report += f"""

FINAL TRUTH:
Can solo developers use this TODAY? {"YES" if overall_percentage >= 80 else "NO"}
Is this v1.0 ready? {"YES" if overall_percentage >= 95 else "NO"}
Should we ship? {"YES" if overall_percentage >= 95 else "NO - FIX ISSUES FIRST"}

{"=" * 80}
END OF BRUTAL ASSESSMENT
{"=" * 80}
"""

        return report


def main():
    """Run the final validation"""
    validator = RFD4FinalValidator()
    results = validator.run_all_tests()
    report = validator.generate_final_report(results)

    print(report)

    # Write report to file
    with open("/mnt/projects/rfd-protocol/RFD4_FINAL_VALIDATION_REPORT.md", "w") as f:
        f.write(report)

    print(
        "\n📄 Full report saved to: /mnt/projects/rfd-protocol/RFD4_FINAL_VALIDATION_REPORT.md"
    )


if __name__ == "__main__":
    main()

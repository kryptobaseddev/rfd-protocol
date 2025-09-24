"""
Cross-Artifact Analysis Engine for RFD
Implements spec-kit style /analyze functionality
"""

from datetime import datetime
from typing import Any, Dict

from .db_utils import get_db_connection


class ArtifactAnalyzer:
    """Analyzes consistency across all project artifacts"""

    def __init__(self, rfd):
        self.rfd = rfd
        self.db_path = rfd.db_path
        self.project_root = rfd.root

    def analyze_cross_artifact_consistency(self) -> Dict[str, Any]:
        """
        Perform comprehensive cross-artifact analysis.
        Similar to spec-kit's /analyze command.

        Checks:
        - Spec to code alignment
        - Task completion vs feature status
        - API contract implementation
        - Test coverage of acceptance criteria
        - Constitution adherence
        - Phase dependencies
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "issues": [],
            "warnings": [],
            "metrics": {},
            "recommendations": [],
        }

        # 1. Check spec to code alignment
        spec_alignment = self._check_spec_alignment()
        results["spec_alignment"] = spec_alignment

        # 2. Check task completion
        task_consistency = self._check_task_consistency()
        results["task_consistency"] = task_consistency

        # 3. Check API contract implementation
        api_implementation = self._check_api_implementation()
        results["api_implementation"] = api_implementation

        # 4. Check test coverage
        test_coverage = self._check_test_coverage()
        results["test_coverage"] = test_coverage

        # 5. Check constitution adherence
        constitution_adherence = self._check_constitution_adherence()
        results["constitution_adherence"] = constitution_adherence

        # 6. Check phase dependencies
        phase_dependencies = self._check_phase_dependencies()
        results["phase_dependencies"] = phase_dependencies

        # 7. Check for hallucinations and drift
        integrity = self._check_integrity()
        results["integrity"] = integrity

        # Calculate overall health
        if results["issues"]:
            results["overall_health"] = "critical"
        elif results["warnings"]:
            results["overall_health"] = "warning"

        return results

    def _check_spec_alignment(self) -> Dict[str, Any]:
        """Check if code aligns with specifications"""
        alignment = {"status": "aligned", "misalignments": []}

        # Load PROJECT.md spec
        spec = self.rfd.load_project_spec()

        # Check each feature
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        for feature in spec.get("features", []):
            # Check if feature exists in database
            cursor.execute(
                """
                SELECT status, description, acceptance
                FROM features WHERE id = ?
            """,
                (feature["id"],),
            )

            row = cursor.fetchone()
            if not row:
                alignment["misalignments"].append(
                    {"feature": feature["id"], "issue": "Feature in spec but not in database"}
                )
                alignment["status"] = "misaligned"
            elif row["status"] != feature.get("status", "pending"):
                alignment["misalignments"].append(
                    {
                        "feature": feature["id"],
                        "issue": f"Status mismatch: spec={feature.get('status')}, db={row['status']}",
                    }
                )
                alignment["status"] = "misaligned"

        conn.close()
        return alignment

    def _check_task_consistency(self) -> Dict[str, Any]:
        """Check task completion vs feature status"""
        consistency = {"status": "consistent", "inconsistencies": []}

        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        # Check features with completed status but incomplete tasks
        cursor.execute(
            """
            SELECT f.id, f.status,
                   COUNT(t.id) as total_tasks,
                   SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
            FROM features f
            LEFT JOIN tasks t ON f.id = t.feature_id
            GROUP BY f.id
            HAVING f.status = 'complete' AND total_tasks > 0 AND completed_tasks < total_tasks
        """
        )

        for row in cursor.fetchall():
            consistency["inconsistencies"].append(
                {
                    "feature": row["id"],
                    "issue": (
                        f"Feature marked complete but has "
                        f"{row['total_tasks'] - row['completed_tasks']} incomplete tasks"
                    ),
                }
            )
            consistency["status"] = "inconsistent"

        # Check for orphaned tasks
        cursor.execute(
            """
            SELECT t.id, t.description
            FROM tasks t
            LEFT JOIN features f ON t.feature_id = f.id
            WHERE f.id IS NULL
        """
        )

        for row in cursor.fetchall():
            consistency["inconsistencies"].append({"task": row["id"], "issue": f"Orphaned task: {row['description']}"})
            consistency["status"] = "inconsistent"

        conn.close()
        return consistency

    def _check_api_implementation(self) -> Dict[str, Any]:
        """Check if API contracts are implemented"""
        implementation = {"status": "implemented", "missing_endpoints": [], "coverage": 0.0}

        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        # Get all API contracts
        cursor.execute(
            """
            SELECT endpoint, method, feature_id, auth_required
            FROM api_contracts
        """
        )

        contracts = cursor.fetchall()
        total = len(contracts)

        if total == 0:
            implementation["coverage"] = 100.0
            conn.close()
            return implementation

        # Check for implementation files (simplified check)
        implemented = 0
        for contract in contracts:
            # Look for route definitions in code
            endpoint = contract["endpoint"]
            method = contract["method"]

            # Search for the endpoint in Python/JS files
            found = False
            for pattern in ["**/*.py", "**/*.js", "**/*.ts"]:
                files = list(self.project_root.glob(pattern))
                for file in files:
                    try:
                        content = file.read_text()
                        if endpoint in content and method in content:
                            found = True
                            break
                    except Exception:
                        continue
                if found:
                    break

            if found:
                implemented += 1
            else:
                implementation["missing_endpoints"].append(
                    {"endpoint": endpoint, "method": method, "feature": contract["feature_id"]}
                )

        implementation["coverage"] = (implemented / total) * 100 if total > 0 else 0

        if implementation["missing_endpoints"]:
            implementation["status"] = "incomplete"

        conn.close()
        return implementation

    def _check_test_coverage(self) -> Dict[str, Any]:
        """Check test coverage of acceptance criteria"""
        coverage = {"status": "covered", "untested_criteria": [], "coverage_percentage": 0.0}

        # Load spec for acceptance criteria
        spec = self.rfd.load_project_spec()

        # Simple heuristic: look for test files
        test_files = []
        for pattern in ["**/test_*.py", "**/*_test.py", "**/*.test.js", "**/*.spec.js"]:
            test_files.extend(list(self.project_root.glob(pattern)))

        if not test_files:
            coverage["status"] = "no_tests"
            coverage["coverage_percentage"] = 0.0
            return coverage

        # Check each feature's acceptance criteria
        tested = 0
        total = 0

        for feature in spec.get("features", []):
            acceptance = feature.get("acceptance", "")
            if not acceptance:
                continue

            total += 1
            found = False

            # Look for acceptance criteria in test files
            for test_file in test_files:
                try:
                    content = test_file.read_text().lower()
                    # Simple check - look for feature id or key acceptance terms
                    if feature["id"].lower() in content or any(
                        term.lower() in content for term in acceptance.split()[:3]
                    ):
                        found = True
                        break
                except Exception:
                    continue

            if found:
                tested += 1
            else:
                coverage["untested_criteria"].append({"feature": feature["id"], "acceptance": acceptance})

        coverage["coverage_percentage"] = (tested / total) * 100 if total > 0 else 0

        if coverage["coverage_percentage"] < 80:
            coverage["status"] = "insufficient"

        return coverage

    def _check_constitution_adherence(self) -> Dict[str, Any]:
        """Check adherence to project constitution"""
        adherence = {"status": "adhered", "violations": []}

        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        # Get constitution principles
        cursor.execute(
            """
            SELECT principle, category
            FROM constitution
            WHERE immutable = 1
        """
        )

        principles = cursor.fetchall()

        # Check for common violations
        for principle in principles:
            if "no mock" in principle["principle"].lower():
                # Check for mock data in non-test files
                for pattern in ["**/*.py", "**/*.js"]:
                    files = [f for f in self.project_root.glob(pattern) if "test" not in f.name.lower()]
                    for file in files:
                        try:
                            content = file.read_text()
                            if any(mock in content for mock in ["mock(", "Mock(", "@patch", "jest.mock"]):
                                adherence["violations"].append(
                                    {
                                        "principle": "No mock data in production",
                                        "file": str(file.relative_to(self.project_root)),
                                        "severity": "high",
                                    }
                                )
                                adherence["status"] = "violated"
                        except Exception:
                            continue

        conn.close()
        return adherence

    def _check_phase_dependencies(self) -> Dict[str, Any]:
        """Check phase dependencies and ordering"""
        dependencies = {"status": "valid", "violations": []}

        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        # Check phase ordering
        cursor.execute(
            """
            SELECT id, name, status, order_index
            FROM project_phases
            ORDER BY order_index
        """
        )

        phases = cursor.fetchall()

        # Check that earlier phases are complete before later ones
        for i, phase in enumerate(phases):
            if phase["status"] in ["active", "complete"]:
                # Check all previous phases
                for j in range(i):
                    if phases[j]["status"] not in ["complete"]:
                        dependencies["violations"].append(
                            {"phase": phase["name"], "issue": f"Started before completing {phases[j]['name']}"}
                        )
                        dependencies["status"] = "violated"

        conn.close()
        return dependencies

    def _check_integrity(self) -> Dict[str, Any]:
        """Check for hallucinations and drift"""
        integrity = {"status": "intact", "hallucinations": 0, "drifts": 0}

        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        # Count hallucinations
        cursor.execute("SELECT COUNT(*) as count FROM hallucination_log")
        integrity["hallucinations"] = cursor.fetchone()["count"]

        # Count unresolved drifts
        cursor.execute("SELECT COUNT(*) as count FROM drift_log WHERE resolved = 0")
        integrity["drifts"] = cursor.fetchone()["count"]

        if integrity["hallucinations"] > 0 or integrity["drifts"] > 0:
            integrity["status"] = "compromised"

        conn.close()
        return integrity

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable analysis report"""
        report = []
        report.append("=" * 60)
        report.append("CROSS-ARTIFACT ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Timestamp: {analysis['timestamp']}")
        report.append(f"Overall Health: {analysis['overall_health'].upper()}")
        report.append("")

        # Spec Alignment
        report.append("📋 SPEC ALIGNMENT")
        spec = analysis.get("spec_alignment", {})
        if spec.get("status") == "aligned":
            report.append("  ✅ All features aligned with specification")
        else:
            report.append(f"  ❌ {len(spec.get('misalignments', []))} misalignments found")
            for misalign in spec.get("misalignments", [])[:3]:
                report.append(f"    - {misalign['feature']}: {misalign['issue']}")
        report.append("")

        # Task Consistency
        report.append("📝 TASK CONSISTENCY")
        tasks = analysis.get("task_consistency", {})
        if tasks.get("status") == "consistent":
            report.append("  ✅ All tasks consistent with feature status")
        else:
            report.append(f"  ❌ {len(tasks.get('inconsistencies', []))} inconsistencies found")
            for inconsistency in tasks.get("inconsistencies", [])[:3]:
                report.append(f"    - {inconsistency.get('issue')}")
        report.append("")

        # API Implementation
        report.append("🔌 API IMPLEMENTATION")
        api = analysis.get("api_implementation", {})
        report.append(f"  Coverage: {api.get('coverage', 0):.1f}%")
        if api.get("missing_endpoints"):
            report.append(f"  ⚠️ {len(api['missing_endpoints'])} endpoints not implemented")
            for endpoint in api.get("missing_endpoints", [])[:3]:
                report.append(f"    - {endpoint['method']} {endpoint['endpoint']}")
        else:
            report.append("  ✅ All endpoints implemented")
        report.append("")

        # Test Coverage
        report.append("🧪 TEST COVERAGE")
        tests = analysis.get("test_coverage", {})
        report.append(f"  Coverage: {tests.get('coverage_percentage', 0):.1f}%")
        if tests.get("untested_criteria"):
            report.append(f"  ⚠️ {len(tests['untested_criteria'])} acceptance criteria untested")
        else:
            report.append("  ✅ All acceptance criteria covered")
        report.append("")

        # Constitution Adherence
        report.append("📜 CONSTITUTION ADHERENCE")
        constitution = analysis.get("constitution_adherence", {})
        if constitution.get("status") == "adhered":
            report.append("  ✅ All principles followed")
        else:
            report.append(f"  ❌ {len(constitution.get('violations', []))} violations found")
            for violation in constitution.get("violations", [])[:3]:
                report.append(f"    - {violation['principle']} in {violation['file']}")
        report.append("")

        # Integrity
        report.append("🛡️ INTEGRITY CHECK")
        integrity = analysis.get("integrity", {})
        report.append(f"  Hallucinations: {integrity.get('hallucinations', 0)}")
        report.append(f"  Unresolved Drifts: {integrity.get('drifts', 0)}")
        if integrity.get("status") == "intact":
            report.append("  ✅ System integrity maintained")
        else:
            report.append("  ⚠️ Integrity issues detected")
        report.append("")

        # Recommendations
        if analysis.get("issues"):
            report.append("🚨 CRITICAL ISSUES")
            for issue in analysis["issues"][:5]:
                report.append(f"  - {issue}")
            report.append("")

        if analysis.get("recommendations"):
            report.append("💡 RECOMMENDATIONS")
            for rec in analysis["recommendations"][:5]:
                report.append(f"  - {rec}")

        return "\n".join(report)

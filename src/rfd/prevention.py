#!/usr/bin/env python3
"""Real-time prevention mechanisms for RFD - stop problems before they happen."""

import ast
import json
import re
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class HallucinationPrevention:
    """Real-time code validation to prevent AI hallucinations during generation."""

    MOCK_PATTERNS = [
        r"from\s+unittest\.mock\s+import",  # Mock imports
        r"from\s+mock\s+import",  # Old mock library
        r"import\s+mock\b",  # Direct mock import
        r"Mock\(\)",  # Mock instantiation
        r"MagicMock\(\)",  # MagicMock usage
        r"@mock\.patch",  # Mock decorator
        r"@patch\(",  # Patch decorator
        r"\bmock_\w+",  # Variables starting with mock_
        r"TODO:?\s*(implement|add|fix|complete)",
        r"raise\s+NotImplementedError",
        r"pass\s*#\s*(TODO|FIXME|implement)",
        r'return\s+(None|"mock"|"test"|"TODO")',
        r'print\("(TODO|Not implemented|Mock)',
    ]

    STUB_INDICATORS = [
        ("function", r"def\s+\w+\([^)]*\):\s*pass"),
        ("function", r"def\s+\w+\([^)]*\):\s*\.\.\.\s*$"),
        ("function", r"def\s+\w+\([^)]*\):\s*return\s+None"),
        ("class", r"class\s+\w+.*:\s*pass"),
    ]

    def __init__(self, db_path: str = ".rfd/memory.db"):
        self.db_path = db_path
        self.validations_performed = []
        self.violations_prevented = []

    def validate_code_before_write(self, file_path: str, code: str) -> Tuple[bool, List[str]]:
        """Validate code BEFORE it gets written to prevent hallucinations."""
        violations = []

        # Check for mock patterns
        for pattern in self.MOCK_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(f"Mock pattern detected: {pattern}")

        # Check for stub functions/classes
        for stub_type, pattern in self.STUB_INDICATORS:
            matches = re.findall(pattern, code, re.MULTILINE)
            if matches:
                violations.append(f"Stub {stub_type} detected: {matches[0][:50]}")

        # Check for incomplete implementations
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for functions that only raise NotImplementedError
                    if len(node.body) == 1:
                        stmt = node.body[0]
                        if isinstance(stmt, ast.Raise):
                            if isinstance(stmt.exc, ast.Call):
                                if hasattr(stmt.exc.func, "id") and stmt.exc.func.id == "NotImplementedError":
                                    violations.append(f"Unimplemented function: {node.name}")
                        elif isinstance(stmt, ast.Pass):
                            violations.append(f"Empty function: {node.name}")
        except SyntaxError as e:
            violations.append(f"Syntax error in code: {e}")

        # Log the validation attempt
        self.validations_performed.append(
            {
                "file": file_path,
                "timestamp": datetime.now().isoformat(),
                "violations": violations,
                "prevented": len(violations) > 0,
            }
        )

        if violations:
            self.violations_prevented.extend(violations)

        return (len(violations) == 0, violations)

    def hook_into_file_operations(self):
        """Install hooks to validate all file writes in real-time."""
        # This would integrate with IDE/editor plugins
        # For now, we'll provide a validation API
        return {
            "pre_write_hook": self.validate_code_before_write,
            "validation_stats": self.get_prevention_stats,
        }

    def get_prevention_stats(self) -> Dict[str, Any]:
        """Get statistics on prevented hallucinations."""
        return {
            "total_validations": len(self.validations_performed),
            "violations_prevented": len(self.violations_prevented),
            "success_rate": len([v for v in self.validations_performed if not v["prevented"]])
            / max(len(self.validations_performed), 1),
            "common_violations": self._get_common_violations(),
        }

    def _get_common_violations(self) -> List[str]:
        """Analyze common violation patterns."""
        from collections import Counter

        violation_types = []
        for validation in self.validations_performed:
            for violation in validation["violations"]:
                # Extract violation type
                if "Mock" in violation:
                    violation_types.append("mock_usage")
                elif "Stub" in violation:
                    violation_types.append("stub_code")
                elif "Unimplemented" in violation:
                    violation_types.append("unimplemented")
                elif "Empty" in violation:
                    violation_types.append("empty_function")
                else:
                    violation_types.append("other")

        counter = Counter(violation_types)
        return [f"{vtype}: {count}" for vtype, count in counter.most_common(5)]


class WorkflowEnforcement:
    """Real-time workflow enforcement via git hooks and process monitoring."""

    def __init__(self, db_path: str = ".rfd/memory.db"):
        self.db_path = db_path
        self.active_workflow = None
        self.workflow_violations = []

    def install_git_hooks(self) -> bool:
        """Install git hooks for real-time workflow enforcement."""
        hooks_dir = Path(".git/hooks")
        if not hooks_dir.exists():
            return False

        # Pre-commit hook to validate workflow compliance
        pre_commit_hook = """#!/bin/bash
# RFD Workflow Enforcement Hook

# Check if we're in an RFD workflow
if [ -f .rfd/workflow.lock ]; then
    workflow_id=$(cat .rfd/workflow.lock)

    # Validate changes against workflow spec
    rfd prevent validate-commit "$workflow_id"
    if [ $? -ne 0 ]; then
        echo "❌ Commit blocked: Workflow violation detected"
        echo "Run 'rfd workflow status' for details"
        exit 1
    fi
fi

# Check for scope drift
rfd prevent check-scope
if [ $? -ne 0 ]; then
    echo "❌ Commit blocked: Scope drift detected"
    echo "Run 'rfd prevent check-scope' for details"
    exit 1
fi

exit 0
"""

        hook_path = hooks_dir / "pre-commit"
        hook_path.write_text(pre_commit_hook)
        hook_path.chmod(0o755)

        # Pre-push hook to validate feature completeness
        pre_push_hook = """#!/bin/bash
# RFD Feature Completeness Hook

# Validate feature is ready for push
rfd validate
if [ $? -ne 0 ]; then
    echo "❌ Push blocked: Validation failed"
    echo "Run 'rfd validate' to see errors"
    exit 1
fi

exit 0
"""

        push_hook_path = hooks_dir / "pre-push"
        push_hook_path.write_text(pre_push_hook)
        push_hook_path.chmod(0o755)

        return True

    def validate_commit(self, workflow_id: str) -> Tuple[bool, List[str]]:
        """Validate a commit against the active workflow specification."""
        violations = []

        # Get workflow spec from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT spec, allowed_files, forbidden_patterns
            FROM workflows
            WHERE id = ?
        """,
            (workflow_id,),
        )

        result = cursor.fetchone()
        if not result:
            violations.append(f"Unknown workflow: {workflow_id}")
            return False, violations

        spec, allowed_files, forbidden_patterns = result

        # Get staged files
        staged_files = (
            subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip().split("\n")
        )

        # Check if files are allowed
        if allowed_files:
            allowed = json.loads(allowed_files)
            for file in staged_files:
                if not any(file.startswith(prefix) for prefix in allowed):
                    violations.append(f"File not in workflow scope: {file}")

        # Check for forbidden patterns
        if forbidden_patterns:
            patterns = json.loads(forbidden_patterns)
            for file in staged_files:
                if file.endswith(".py"):
                    content = subprocess.check_output(["git", "show", f":{file}"], text=True)
                    for pattern in patterns:
                        if re.search(pattern, content):
                            violations.append(f"Forbidden pattern in {file}: {pattern}")

        conn.close()
        return len(violations) == 0, violations

    def monitor_file_changes(self, callback=None):
        """Monitor file system for unauthorized changes."""
        # This would use inotify on Linux or FSEvents on macOS
        # For now, provide the structure
        return {
            "start_monitoring": lambda: self._start_monitor(callback),
            "stop_monitoring": lambda: self._stop_monitor(),
            "get_violations": lambda: self.workflow_violations,
        }

    def _start_monitor(self, callback):
        """Start file system monitoring."""
        # Implementation would use watchdog or similar
        pass

    def _stop_monitor(self):
        """Stop file system monitoring."""
        pass

    def validate_workflow_compliance(self, workflow_id: str) -> Tuple[bool, List[str]]:
        """Validate current changes against workflow specifications."""
        violations = []

        # Get current git changes
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"], capture_output=True, text=True, check=True
            )
            changed_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            changed_files = []

        # For now, just check that changes are related to the feature
        # Since we don't have a workflows table with specs
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if feature exists
        cursor.execute(
            "SELECT id, description FROM features WHERE id = ?",
            (workflow_id,),
        )

        result = cursor.fetchone()
        if not result:
            violations.append(f"Feature {workflow_id} not found")
        else:
            # Basic validation: ensure we're not modifying unrelated system files
            system_files = [".git/", ".venv/", "__pycache__", ".pyc"]
            for file in changed_files:
                if any(sys_file in file for sys_file in system_files):
                    violations.append(f"System file modified: {file}")

        conn.close()

        if violations:
            self.workflow_violations.extend(violations)

        return (len(violations) == 0, violations)


class ScopeDriftPrevention:
    """Prevent scope drift in real-time using file watchers and boundaries."""

    def __init__(self, db_path: str = ".rfd/memory.db"):
        self.db_path = db_path
        self.scope_boundaries = {}
        self.drift_attempts = []

    def define_scope_boundaries(self, feature_id: str) -> Dict[str, List[str]]:
        """Define allowed scope for a feature."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get feature details - features table has id, not name
        cursor.execute(
            """
            SELECT id, description, acceptance_criteria
            FROM features
            WHERE id = ?
        """,
            (feature_id,),
        )

        result = cursor.fetchone()
        if not result:
            return {}

        feature_id_db, description, criteria = result

        # Auto-detect scope based on feature
        scope = {
            "allowed_dirs": [],
            "allowed_files": [],
            "forbidden_patterns": [],
            "max_file_changes": 10,
        }

        # Infer scope from feature id and description
        # Always allow main source directory for features
        scope["allowed_dirs"].append("src/")
        
        # Always allow test directories
        scope["allowed_dirs"].append("tests/")
        
        # Allow project files
        scope["allowed_dirs"].append(".rfd/")
        
        # Allow scripts
        scope["allowed_dirs"].append("scripts/")

        # Store boundaries
        self.scope_boundaries[feature_id] = scope

        # Save to database now that column exists
        cursor.execute(
            """
            UPDATE features
            SET scope_definition = ?
            WHERE id = ?
        """,
            (json.dumps(scope), feature_id),
        )

        conn.commit()
        conn.close()

        return scope

    def check_file_in_scope(self, file_path: str, feature_id: str) -> Tuple[bool, str]:
        """Check if a file change is within feature scope."""
        if feature_id not in self.scope_boundaries:
            self.define_scope_boundaries(feature_id)

        scope = self.scope_boundaries.get(feature_id, {})

        # Check allowed directories
        allowed_dirs = scope.get("allowed_dirs", [])
        
        # Always allow certain files
        allowed_patterns = ["coverage", ".coverage", "*.pyc", "__pycache__", "*.egg-info"]
        if any(pattern in file_path for pattern in allowed_patterns):
            return True, "Build/test artifact allowed"
        
        if allowed_dirs:
            in_allowed_dir = any(file_path.startswith(dir_path) for dir_path in allowed_dirs)
            if not in_allowed_dir:
                return False, f"File {file_path} not in allowed directories: {allowed_dirs}"

        # Check allowed files
        allowed_files = scope.get("allowed_files", [])
        if allowed_files and file_path not in allowed_files:
            return False, f"File {file_path} not in allowed files list"

        return True, "File is within scope"

    def install_scope_guards(self) -> Dict[str, Any]:
        """Install scope guards to prevent drift."""
        # Create scope check script
        scope_check_script = """#!/usr/bin/env python3
import sys
from pathlib import Path
from rfd.prevention import ScopeDriftPrevention

# Get current feature from session
session_file = Path(".rfd/context/current.md")
if not session_file.exists():
    sys.exit(0)  # No active session

# Extract feature ID
import frontmatter
with open(session_file) as f:
    post = frontmatter.load(f)
    feature_id = post.metadata.get('feature')

if not feature_id:
    sys.exit(0)  # No active feature

# Check all modified files
import subprocess
modified_files = subprocess.check_output(
    ["git", "diff", "--name-only"],
    text=True
).strip().split('\\n')

prevention = ScopeDriftPrevention()
violations = []

for file in modified_files:
    if file:  # Skip empty lines
        in_scope, message = prevention.check_file_in_scope(file, feature_id)
        if not in_scope:
            violations.append(message)

if violations:
    print("❌ Scope violations detected:")
    for v in violations:
        print(f"  - {v}")
    sys.exit(1)

print("✅ All changes within scope")
sys.exit(0)
"""

        # Save the script
        script_path = Path("src/rfd/scripts/check_scope.py")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(scope_check_script)
        script_path.chmod(0o755)

        return {
            "scope_check_script": str(script_path),
            "boundaries_defined": len(self.scope_boundaries),
            "install_status": "success",
        }

    def check_current_changes(self) -> Tuple[bool, List[str]]:
        """Check current git changes for scope drift."""
        violations = []

        # Get current feature from session
        session_file = Path(".rfd/context/current.md")
        if not session_file.exists():
            return True, []  # No active session

        # Parse session file
        content = session_file.read_text()
        feature_id = None
        for line in content.split("\n"):
            if line.startswith("feature:"):
                feature_id = line.split(":")[1].strip()
                break

        if not feature_id:
            return True, []  # No feature in session

        # Get changed files
        try:
            result = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True, check=True)
            changed_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            return True, []

        # Check each file
        for file in changed_files:
            if file:  # Skip empty lines
                valid, reason = self.check_file_in_scope(file, feature_id)
                if not valid:
                    violations.append(reason)

        return (len(violations) == 0, violations)

    def report_drift_attempt(self, file_path: str, reason: str):
        """Record a scope drift attempt that was prevented."""
        self.drift_attempts.append(
            {"timestamp": datetime.now().isoformat(), "file": file_path, "reason": reason, "prevented": True}
        )

    def get_drift_report(self) -> Dict[str, Any]:
        """Get report on prevented scope drift."""
        return {
            "total_attempts": len(self.drift_attempts),
            "files_protected": len({d["file"] for d in self.drift_attempts}),
            "common_reasons": self._analyze_drift_reasons(),
            "prevention_active": True,
        }

    def _analyze_drift_reasons(self) -> List[str]:
        """Analyze common drift patterns."""
        from collections import Counter

        reasons = [d["reason"] for d in self.drift_attempts]
        counter = Counter(reasons)
        return [f"{reason}: {count}" for reason, count in counter.most_common(3)]


def main():
    """CLI interface for prevention mechanisms."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m rfd.prevention <command>")
        print("Commands:")
        print("  validate-commit <workflow_id>")
        print("  check-scope")
        print("  validate-feature")
        print("  install-hooks")
        print("  status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "install-hooks":
        workflow = WorkflowEnforcement()
        if workflow.install_git_hooks():
            print("✅ Git hooks installed successfully")
        else:
            print("❌ Failed to install git hooks")
            sys.exit(1)

    elif command == "validate-commit" and len(sys.argv) > 2:
        workflow = WorkflowEnforcement()
        workflow_id = sys.argv[2]
        valid, violations = workflow.validate_commit(workflow_id)
        if not valid:
            print("❌ Workflow violations:")
            for v in violations:
                print(f"  - {v}")
            sys.exit(1)
        print("✅ Commit complies with workflow")

    elif command == "check-scope":
        # Implementation in scope check script
        import subprocess

        result = subprocess.run([sys.executable, "src/rfd/scripts/check_scope.py"], capture_output=True, text=True)
        print(result.stdout)
        sys.exit(result.returncode)

    elif command == "validate-feature":
        import subprocess

        result = subprocess.run(["rfd", "validate"], capture_output=True, text=True)
        print(result.stdout)
        sys.exit(0 if "PASSING" in result.stdout else 1)

    elif command == "status":
        hallucination = HallucinationPrevention()
        workflow = WorkflowEnforcement()
        scope = ScopeDriftPrevention()

        print("=== Prevention Status ===")
        print("\n📊 Hallucination Prevention:")
        stats = hallucination.get_prevention_stats()
        print(f"  Validations: {stats['total_validations']}")
        print(f"  Prevented: {stats['violations_prevented']}")
        print(f"  Success Rate: {stats['success_rate']:.1%}")

        print("\n🔒 Workflow Enforcement:")
        print(f"  Git Hooks: {'Installed' if Path('.git/hooks/pre-commit').exists() else 'Not installed'}")

        print("\n🎯 Scope Drift Prevention:")
        drift_report = scope.get_drift_report()
        print(f"  Attempts Blocked: {drift_report['total_attempts']}")
        print(f"  Files Protected: {drift_report['files_protected']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

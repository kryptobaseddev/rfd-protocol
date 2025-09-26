"""
Spec-Kit Style Integration for RFD
Brings the best of GitHub's spec-kit into RFD
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List


class SpecKitIntegration:
    """Integrates spec-kit style workflow into RFD"""

    def __init__(self, rfd):
        self.rfd = rfd
        # All directories should be under .rfd/ for proper encapsulation
        self.specs_dir = self.rfd.rfd_dir / "specs"
        self.memory_dir = self.rfd.rfd_dir / "memory"
        self.templates_dir = self.rfd.rfd_dir / "templates"

        # Create directories
        self.specs_dir.mkdir(exist_ok=True)
        self.memory_dir.mkdir(exist_ok=True)

    def create_constitution(self) -> bool:
        """
        Store project constitution in database (immutable principles)
        No more file-based constitution!
        """
        from .db_utils import get_db_connection

        conn = get_db_connection(self.rfd.db_path)
        try:
            # Check if constitution already exists
            existing = conn.execute("SELECT COUNT(*) FROM constitution").fetchone()[0]
            if existing > 0:
                print("Constitution already exists in database")
                return True

            self.rfd.load_project_spec()

            # Store core principles in database
            principles = [
                ("Code must run and pass tests before considered complete", "Reality First"),
                ("One feature at a time, complete current work before starting new", "Single Responsibility"),
                ("Specification before implementation, intent drives development", "Spec-Driven"),
                ("No mock data in production code or tests", "No Mocks"),
                ("AI claims must be validated, no lying about completions", "No Hallucination"),
            ]

            for principle, category in principles:
                conn.execute("INSERT INTO constitution (principle, category) VALUES (?, ?)", (principle, category))

            conn.commit()
            print("✅ Stored constitution in database")
            return True
        finally:
            conn.close()

    def specify_feature(self, feature_id: str) -> Path:
        """
        Create detailed specification for a feature
        Like spec-kit's /specify command
        """
        # Get feature from PROJECT.md
        spec = self.rfd.load_project_spec()
        feature = None

        for f in spec.get("features", []):
            if f["id"] == feature_id:
                feature = f
                break

        if not feature:
            raise ValueError(f"Feature {feature_id} not found in PROJECT.md")

        # Create feature directory
        feature_num = spec.get("features", []).index(feature) + 1
        feature_dir = self.specs_dir / f"{feature_num:03d}-{feature_id}"
        feature_dir.mkdir(exist_ok=True)

        # Create spec.md
        spec_file = feature_dir / "spec.md"

        spec_content = f"""# Feature Specification: {feature["description"]}
Feature ID: {feature_id}
Created: {datetime.now().isoformat()}
Status: {feature.get("status", "pending")}

## Overview
{feature["description"]}

## Acceptance Criteria
{feature.get("acceptance", "Not specified")}

## User Journey
1. User initiates {feature_id}
2. System validates input
3. Processing occurs
4. User receives confirmation
5. State is persisted

## Success Scenarios
- Happy path: [describe ideal flow]
- Edge case 1: [describe edge case]
- Edge case 2: [describe edge case]

## Failure Scenarios
- Invalid input: [what happens]
- System unavailable: [fallback behavior]
- Partial failure: [recovery strategy]

## Data Requirements
- Input: [what data is needed]
- Output: [what is produced]
- Storage: [what is persisted]

## Dependencies
- Prerequisites: [what must exist first]
- External systems: [what we depend on]
- Libraries: [required packages]

## Validation Rules
- Input validation: [rules]
- Business logic: [constraints]
- Output validation: [checks]

## Performance Requirements
- Response time: < 200ms
- Throughput: [requests/second]
- Storage: [limits]

## Security Considerations
- Authentication: [required/not required]
- Authorization: [who can access]
- Data protection: [encryption/sanitization]

## Testing Strategy
- Unit tests: [what to test]
- Integration tests: [interactions]
- Acceptance tests: [user scenarios]

## Notes
[Additional context or clarifications]
"""

        spec_file.write_text(spec_content)
        print(f"✅ Created specification at {spec_file}")
        return spec_file

    def create_plan(self, feature_id: str) -> Path:
        """
        Create technical implementation plan
        Like spec-kit's /plan command
        """
        spec = self.rfd.load_project_spec()
        feature = None

        for f in spec.get("features", []):
            if f["id"] == feature_id:
                feature = f
                break

        if not feature:
            raise ValueError(f"Feature {feature_id} not found")

        feature_num = spec.get("features", []).index(feature) + 1
        feature_dir = self.specs_dir / f"{feature_num:03d}-{feature_id}"
        feature_dir.mkdir(exist_ok=True)

        plan_file = feature_dir / "plan.md"

        plan_content = f"""# Implementation Plan: {feature_id}
Created: {datetime.now().isoformat()}

## Constitutional Compliance
This plan adheres to all principles in memory/constitution.md

## Technical Translation
Specification → Implementation mapping

### Components Required
1. **Data Models**
   - [Model 1]: [fields and types]
   - [Model 2]: [fields and types]

2. **Business Logic**
   - [Function 1]: [input] → [output]
   - [Function 2]: [input] → [output]

3. **API Endpoints** (if applicable)
   - POST /endpoint: [purpose]
   - GET /endpoint: [purpose]

4. **Database Schema**
   ```sql
   CREATE TABLE [table_name] (
     id INTEGER PRIMARY KEY,
     -- fields
   );
   ```

## Implementation Sequence
1. Create data models
2. Implement core logic
3. Add API endpoints
4. Write tests
5. Add validation
6. Handle errors
7. Optimize if needed

## File Structure
```
src/
  {feature_id}/
    __init__.py
    models.py
    logic.py
    api.py
    validators.py
tests/
  test_{feature_id}.py
```

## Validation Checkpoints
- [ ] Data models created
- [ ] Core logic implemented
- [ ] API endpoints working
- [ ] Tests passing
- [ ] Acceptance criteria met
- [ ] No mock data
- [ ] No hallucinations detected

## Risk Mitigation
- Risk 1: [description] → [mitigation]
- Risk 2: [description] → [mitigation]

## Success Criteria
- All acceptance tests pass
- No AI hallucinations detected
- Real data only (no mocks)
- Performance requirements met
"""

        plan_file.write_text(plan_content)
        print(f"✅ Created plan at {plan_file}")
        return plan_file

    def create_tasks(self, feature_id: str) -> Path:
        """
        Generate executable tasks from plan
        Like spec-kit's /tasks command
        """
        spec = self.rfd.load_project_spec()
        feature = None

        for f in spec.get("features", []):
            if f["id"] == feature_id:
                feature = f
                break

        if not feature:
            raise ValueError(f"Feature {feature_id} not found")

        feature_num = spec.get("features", []).index(feature) + 1
        feature_dir = self.specs_dir / f"{feature_num:03d}-{feature_id}"
        feature_dir.mkdir(exist_ok=True)

        tasks_file = feature_dir / "tasks.md"

        # Parse acceptance criteria to generate tasks
        acceptance = feature.get("acceptance", "")
        tasks = self._generate_tasks_from_acceptance(acceptance)

        tasks_content = f"""# Tasks: {feature_id}
Generated: {datetime.now().isoformat()}

## Task List
[P] = Can be done in parallel
[S] = Must be done sequentially

### Phase 1: Setup
- [P] Create directory structure for {feature_id}
- [P] Initialize test file test_{feature_id}.py
- [P] Create __init__.py files

### Phase 2: Core Implementation
"""

        for i, task in enumerate(tasks, 1):
            tasks_content += f"- [S] Task {i}: {task}\n"

        tasks_content += f"""
### Phase 3: Validation
- [S] Run acceptance tests
- [S] Validate against specification
- [S] Check for AI hallucinations
- [S] Verify no mock data

### Phase 4: Integration
- [S] Integrate with existing codebase
- [S] Update documentation
- [S] Run full test suite

## Execution Commands
```bash
# After each task, validate:
rfd validate --feature {feature_id}

# If validation fails:
rfd revert

# When all tasks complete:
rfd complete {feature_id}
```

## Success Checklist
- [ ] All tasks completed
- [ ] Acceptance criteria met
- [ ] Tests passing
- [ ] No hallucinations detected
- [ ] No mock data present
- [ ] Code reviewed and approved
"""

        tasks_file.write_text(tasks_content)

        # Also create tasks in database
        self._store_tasks_in_db(feature_id, tasks)

        print(f"✅ Created tasks at {tasks_file}")
        return tasks_file

    def _generate_tasks_from_acceptance(self, acceptance: str) -> List[str]:
        """Generate tasks from acceptance criteria"""
        tasks = []

        for line in acceptance.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Parse different criteria types into tasks
            if "endpoint:" in line.lower():
                # "endpoint: POST /login returns 200"
                tasks.append(f"Implement {line}")
                tasks.append(f"Write test for {line}")
            elif "database:" in line.lower():
                # "database: users table exists"
                tasks.append(f"Create {line}")
                tasks.append(f"Add migration for {line}")
            elif "test:" in line.lower():
                # "test: test_user_login passes"
                test_name = line.split(":")[1].strip()
                tasks.append(f"Implement functionality to make {test_name} pass")
            elif "function:" in line.lower() or "creates:" in line.lower():
                tasks.append(f"Implement {line}")
            else:
                # Generic criterion
                tasks.append(f"Ensure: {line}")

        return (
            tasks
            if tasks
            else [
                "Implement core functionality",
                "Write tests",
                "Validate implementation",
            ]
        )

    def _store_tasks_in_db(self, feature_id: str, tasks: List[str]):
        """Store tasks in database for tracking"""
        conn = sqlite3.connect(self.rfd.db_path)

        # Clear existing tasks for this feature
        conn.execute("DELETE FROM tasks WHERE feature_id = ?", (feature_id,))

        # Insert new tasks
        for task in tasks:
            conn.execute(
                """
                INSERT INTO tasks (feature_id, description, status, created_at)
                VALUES (?, ?, 'pending', ?)
            """,
                (feature_id, task, datetime.now().isoformat()),
            )

        conn.commit()
        conn.close()

    def clarify(self, feature_id: str, question: str) -> str:
        """
        Clarify specification ambiguities
        Like spec-kit's /clarify command
        """
        feature_num = 1  # Would calculate from feature list
        feature_dir = self.specs_dir / f"{feature_num:03d}-{feature_id}"
        clarifications_file = feature_dir / "clarifications.md"

        # Append clarification
        timestamp = datetime.now().isoformat()
        clarification = f"\n## {timestamp}\n**Q**: {question}\n**A**: [To be resolved]\n"

        if clarifications_file.exists():
            existing = clarifications_file.read_text()
            clarifications_file.write_text(existing + clarification)
        else:
            header = f"# Clarifications: {feature_id}\n"
            clarifications_file.write_text(header + clarification)

        return f"Clarification recorded. Please resolve in {clarifications_file}"

    def implement_feature(self, feature_id: str) -> bool:
        """
        Execute implementation with validation at each step
        Like spec-kit's /implement command
        """
        # Load tasks
        conn = sqlite3.connect(self.rfd.db_path)
        tasks = conn.execute(
            """
            SELECT id, description, status FROM tasks
            WHERE feature_id = ?
            ORDER BY created_at
        """,
            (feature_id,),
        ).fetchall()
        conn.close()

        if not tasks:
            print(f"No tasks found for {feature_id}. Run 'rfd speckit tasks {feature_id}' first.")
            return False

        print(f"\n🚀 Implementing {feature_id} ({len(tasks)} tasks)")

        for task_id, description, status in tasks:
            if status == "complete":
                print(f"✅ Already complete: {description}")
                continue

            print(f"\n📝 Task: {description}")
            print("Implement this task, then press Enter to validate...")
            input()  # Wait for manual implementation

            # Validate after each task
            validation_result = self.rfd.validator.validate(feature=feature_id)

            if validation_result["passing"]:
                # Mark task complete
                conn = sqlite3.connect(self.rfd.db_path)
                conn.execute(
                    """
                    UPDATE tasks SET status = 'complete', completed_at = ?
                    WHERE id = ?
                """,
                    (datetime.now().isoformat(), task_id),
                )
                conn.commit()
                conn.close()
                print("✅ Task validated and marked complete")
            else:
                print("❌ Validation failed. Fix issues before continuing.")
                return False

        print(f"\n✨ All tasks complete for {feature_id}!")
        return True

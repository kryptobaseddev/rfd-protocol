"""
Specification Formatting Module
Handles formatting of various specification documents
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import frontmatter


class ProjectPhase:
    def __init__(self, id: str, name: str, type: str, duration_weeks: int):
        self.id = id
        self.name = name
        self.type = type
        self.duration_weeks = duration_weeks
        self.dependencies = []
        self.deliverables = []
        self.tasks = []
        self.acceptance_criteria = []


class TechStackDecision:
    def __init__(self, category: str, choice: str, rationale: str):
        self.category = category
        self.choice = choice
        self.rationale = rationale
        self.alternatives_considered = []
        self.constraints = []
        self.risks = []


class APIEndpoint:
    def __init__(self, method: str, path: str, description: str):
        self.method = method
        self.path = path
        self.description = description
        self.auth_required = False
        self.rate_limit = None
        self.request_schema = {}
        self.response_schema = {}
        self.errors = []
        self.validation_rules = []


class SpecFormatter:
    """Formats various specification documents"""

    def format_phases_document(self, phases: List[ProjectPhase]) -> str:
        """Format phases into markdown document"""
        doc = "# Project Phases\n\n"

        total_weeks = sum(p.duration_weeks for p in phases)
        doc += f"**Total Duration**: {total_weeks} weeks\n\n"

        doc += "## Phase Overview\n\n"
        doc += "| Phase | Type | Duration | Dependencies |\n"
        doc += "|-------|------|----------|-------------|\n"

        for phase in phases:
            deps = ", ".join(phase.dependencies) if phase.dependencies else "None"
            doc += f"| {phase.name} | {phase.type} | {phase.duration_weeks} weeks | {deps} |\n"

        doc += "\n## Detailed Phases\n\n"

        for phase in phases:
            doc += f"### {phase.name}\n"
            doc += f"**ID**: {phase.id}\n"
            doc += f"**Type**: {phase.type}\n"
            doc += f"**Duration**: {phase.duration_weeks} weeks\n\n"

            if phase.dependencies:
                doc += f"**Dependencies**: {', '.join(phase.dependencies)}\n\n"

            doc += "#### Deliverables\n"
            for deliverable in phase.deliverables:
                doc += f"- {deliverable}\n"

            doc += "\n#### Tasks\n"
            for task in phase.tasks:
                doc += f"- [ ] {task['name']} ({task['hours']}h)\n"

            doc += "\n#### Acceptance Criteria\n"
            for criteria in phase.acceptance_criteria:
                doc += f"- {criteria}\n"

            doc += "\n---\n\n"

        return doc

    def format_adr(self, tech_stack: List[TechStackDecision]) -> str:
        """Format Architecture Decision Record"""
        doc = f"""# ADR-001: Technology Stack Selection

**Date**: {datetime.now().strftime("%Y-%m-%d")}
**Status**: Proposed

## Context
We need to select the technology stack for the project implementation.

## Decisions

"""
        for decision in tech_stack:
            doc += f"### {decision.category.capitalize()}: {decision.choice}\n\n"
            doc += f"**Rationale**: {decision.rationale}\n\n"

            if decision.alternatives_considered:
                doc += "**Alternatives Considered**:\n"
                for alt in decision.alternatives_considered:
                    doc += f"- {alt}\n"
                doc += "\n"

            if decision.constraints:
                doc += "**Constraints**:\n"
                for constraint in decision.constraints:
                    doc += f"- {constraint}\n"
                doc += "\n"

            if decision.risks:
                doc += "**Risks**:\n"
                for risk in decision.risks:
                    doc += f"- {risk}\n"
                doc += "\n"

        doc += """## Consequences

### Positive
- Technology choices aligned with project requirements
- Clear rationale for decisions
- Team can prepare for identified constraints

### Negative
- Some learning curve expected
- Potential risks need mitigation strategies

## References
- Project requirements document
- Team skill assessment
- Technology evaluation criteria
"""
        return doc

    def format_api_document(self, endpoints: List[APIEndpoint]) -> str:
        """Format API contract document"""
        doc = "# API Contract Specification\n\n"
        doc += "**Version**: 1.0.0\n"
        doc += f"**Generated**: {datetime.now().isoformat()}\n\n"

        doc += "## Endpoints\n\n"

        for endpoint in endpoints:
            doc += f"### {endpoint.method} {endpoint.path}\n"
            doc += f"{endpoint.description}\n\n"

            doc += "**Authentication**: "
            doc += "Required\n" if endpoint.auth_required else "Not required\n"

            if endpoint.rate_limit:
                doc += f"**Rate Limit**: {endpoint.rate_limit}\n"

            doc += "\n**Request**:\n```json\n"
            doc += json.dumps(endpoint.request_schema, indent=2)
            doc += "\n```\n\n"

            doc += "**Response**:\n```json\n"
            doc += json.dumps(endpoint.response_schema, indent=2)
            doc += "\n```\n\n"

            if endpoint.errors:
                doc += "**Error Responses**:\n"
                for error in endpoint.errors:
                    doc += f"- `{error['code']}`: {error['message']}\n"

            doc += "\n---\n\n"

        return doc

    def update_project_md(
        self,
        project_info: Dict[str, Any],
        phases: List[ProjectPhase],
        tech_stack: List[TechStackDecision],
        api_endpoints: List[APIEndpoint],
    ):
        """Update PROJECT.md with comprehensive specification"""
        project_file = Path("PROJECT.md")

        if project_file.exists():
            with open(project_file) as f:
                post = frontmatter.load(f)
        else:
            post = frontmatter.Post("")

        # Update metadata
        post.metadata.update(
            {
                "name": project_info["name"],
                "description": project_info["description"],
                "version": "0.1.0",
                "development_mode": "0-to-1",
                "generated_at": datetime.now().isoformat(),
            }
        )

        # Update stack
        stack_dict = {}
        for decision in tech_stack:
            stack_dict[decision.category] = decision.choice
        post.metadata["stack"] = stack_dict

        # Add phases summary
        post.metadata["phases"] = [
            {
                "id": p.id,
                "name": p.name,
                "duration_weeks": p.duration_weeks,
                "task_count": len(p.tasks),
            }
            for p in phases
        ]

        # Add API summary
        post.metadata["api_endpoints_count"] = len(api_endpoints)

        # Add specs references
        post.metadata["specifications"] = {
            "constitution": "specs/CONSTITUTION.md",
            "phases": "specs/PHASES.md",
            "tech_adr": "specs/ADR-001-tech-stack.md",
            "api_contract": "specs/API_CONTRACT.md",
            "guidelines": "specs/DEVELOPMENT_GUIDELINES.md",
        }

        # Write back
        with open(project_file, "w") as f:
            f.write(frontmatter.dumps(post))

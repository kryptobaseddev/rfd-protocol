"""
Comprehensive Spec Generation System for RFD
Combines RFD's reality-first approach with spec-kit's planning methodologies
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import frontmatter

try:
    from .spec_formatter import (
        APIEndpoint,
        ProjectPhase,
        SpecFormatter,
        TechStackDecision,
    )
except ImportError:
    from spec_formatter import (
        APIEndpoint,
        ProjectPhase,
        SpecFormatter,
        TechStackDecision,
    )


class SpecGenerator:
    """Generates comprehensive project specifications"""

    def __init__(self, rfd):
        self.rfd = rfd
        self.specs_dir = Path("specs")
        self.specs_dir.mkdir(exist_ok=True)
        self.formatter = SpecFormatter()

    def ingest_prd(self, prd_path: Path) -> Dict[str, Any]:
        """Ingest and parse PRD document"""
        if not prd_path.exists():
            raise FileNotFoundError(f"PRD not found: {prd_path}")

        with open(prd_path) as f:
            content = f.read()

        # Check if it's frontmatter format
        if content.startswith("---"):
            post = frontmatter.loads(content)
            return self._parse_frontmatter_prd(post)
        else:
            return self._parse_text_prd(content)

    def _parse_text_prd(self, content: str) -> Dict[str, Any]:
        """Parse plain text PRD"""
        lines = content.split("\n")
        project_info = {
            "name": "",
            "description": "",
            "problem": "",
            "solution": "",
            "target_users": [],
            "core_features": [],
            "requirements": [],
            "constraints": [],
            "success_metrics": [],
        }

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("# "):
                project_info["name"] = line[2:].strip()
            elif line.startswith("## Problem"):
                current_section = "problem"
            elif line.startswith("## Solution"):
                current_section = "solution"
            elif line.startswith("## Target Users"):
                current_section = "target_users"
            elif line.startswith("## Core Features"):
                current_section = "core_features"
            elif line.startswith("## Requirements"):
                current_section = "requirements"
            elif line.startswith("## Constraints"):
                current_section = "constraints"
            elif line.startswith("## Success Metrics"):
                current_section = "success_metrics"
            elif line.startswith("## "):
                current_section = None
            elif line and current_section:
                if current_section in ["problem", "solution"]:
                    project_info[current_section] += line + " "
                elif line.startswith("- "):
                    if isinstance(project_info[current_section], list):
                        project_info[current_section].append(line[2:].strip())

        # Clean up text fields
        project_info["problem"] = project_info["problem"].strip()
        project_info["solution"] = project_info["solution"].strip()

        return project_info

    def _parse_frontmatter_prd(self, post: frontmatter.Post) -> Dict[str, Any]:
        """Parse frontmatter format PRD"""
        return {
            "name": post.metadata.get("name", ""),
            "description": post.metadata.get("description", ""),
            "problem": post.metadata.get("problem", ""),
            "solution": post.metadata.get("solution", ""),
            "target_users": post.metadata.get("target_users", []),
            "core_features": post.metadata.get("core_features", []),
            "requirements": post.metadata.get("requirements", []),
            "constraints": post.metadata.get("constraints", []),
            "success_metrics": post.metadata.get("success_metrics", []),
        }

    def generate_project_constitution(self, project_info: Dict[str, Any]) -> str:
        """Generate PROJECT CONSTITUTION document"""

        constitution = f"""# PROJECT CONSTITUTION
**{project_info["name"].upper()}**
*Generated: {datetime.now().strftime("%Y-%m-%d")}*

## IMMUTABLE PRINCIPLES

### Core Purpose
{project_info["problem"]}

**Solution Approach**: {project_info["solution"]}

### Non-Negotiable Requirements
"""
        for req in project_info.get("requirements", [])[:5]:
            constitution += f"1. {req}\n"

        constitution += """
## DEVELOPMENT PHILOSOPHY

### Reality-First Development
- Every feature must be validated through working code
- No assumptions without implementation proof
- Test with real data, never mocks in production
- If it's not tested, it doesn't exist

### Progressive Enhancement
- Start with core functionality that works
- Add features only after foundation is solid
- Each iteration must maintain system stability
- Never break working features for new ones

## PROJECT BOUNDARIES

### What This Project IS
"""
        for feature in project_info.get("core_features", []):
            constitution += f"- {feature}\n"

        constitution += """
### What This Project IS NOT
- Not a framework or library
- Not trying to solve every problem
- Not optimizing prematurely
- Not adding features without clear requirements

## SUCCESS CRITERIA

### Measurable Outcomes
"""
        for metric in project_info.get("success_metrics", []):
            constitution += f"- {metric}\n"

        constitution += """
### Quality Gates
- ✅ All tests must pass before merge
- ✅ Code coverage must not decrease
- ✅ Performance benchmarks must be met
- ✅ Security vulnerabilities must be addressed

## DECISION FRAMEWORK

### When Making Decisions, Ask:
1. Does this align with our core purpose?
2. Can we validate this works with code?
3. Does this maintain or improve system stability?
4. Is this the simplest solution that works?
5. Have we tested this with real scenarios?

### Red Flags to Avoid
- 🚫 "We'll fix it later"
- 🚫 "It works on my machine"
- 🚫 "We don't need tests for this"
- 🚫 "Let's add this just in case"
- 🚫 "The AI said it would work"

## TEAM AGREEMENTS

### Development Practices
- Write tests first (TDD when possible)
- Document why, not just what
- Review code within 24 hours
- Fix bugs before adding features
- Refactor only with test coverage

### Communication Principles
- Assume positive intent
- Provide actionable feedback
- Share context, not just conclusions
- Escalate blockers immediately
- Celebrate working code

---
*This constitution is our North Star. When in doubt, refer back to these principles.*
"""
        return constitution

    def generate_phase_breakdown(self, project_info: Dict[str, Any]) -> List[ProjectPhase]:
        """Generate development phases based on project info"""
        phases = []

        # Phase 0: Foundation
        foundation = ProjectPhase(id="phase-0", name="Foundation & Setup", type="planning", duration_weeks=1)
        foundation.dependencies = []
        foundation.deliverables = [
            "Development environment setup",
            "Repository structure",
            "CI/CD pipeline",
            "Testing framework",
            "Documentation structure",
        ]
        foundation.tasks = [
            {"name": "Setup repository", "hours": 2},
            {"name": "Configure dev environment", "hours": 4},
            {"name": "Setup CI/CD", "hours": 6},
            {"name": "Create testing framework", "hours": 4},
            {"name": "Initialize documentation", "hours": 2},
        ]
        foundation.acceptance_criteria = [
            "Repository is accessible to all team members",
            "CI/CD runs on every commit",
            "Tests can be run locally and in CI",
            "README contains setup instructions",
        ]
        phases.append(foundation)

        # Phase 1: Core Data Model
        data_model = ProjectPhase(id="phase-1", name="Core Data Model", type="development", duration_weeks=2)
        data_model.dependencies = ["phase-0"]
        data_model.deliverables = [
            "Database schema",
            "Data models",
            "Validation logic",
            "Migration scripts",
            "Model tests",
        ]
        data_model.tasks = [
            {"name": "Design database schema", "hours": 8},
            {"name": "Implement data models", "hours": 12},
            {"name": "Create validation logic", "hours": 8},
            {"name": "Write migration scripts", "hours": 4},
            {"name": "Test data layer", "hours": 8},
        ]
        data_model.acceptance_criteria = [
            "All models have validation",
            "Database migrations work",
            "100% test coverage for models",
            "CRUD operations functional",
        ]
        phases.append(data_model)

        # Generate feature phases based on core features
        for i, feature in enumerate(project_info.get("core_features", [])[:5], 2):
            feature_phase = ProjectPhase(
                id=f"phase-{i}",
                name=f"Feature: {feature[:50]}",
                type="development",
                duration_weeks=2,
            )
            feature_phase.dependencies = [f"phase-{i - 1}"]
            feature_phase.deliverables = [
                f"Working {feature} implementation",
                "Feature tests",
                "API endpoints (if applicable)",
                "Documentation",
                "Integration tests",
            ]
            feature_phase.tasks = [
                {"name": f"Design {feature}", "hours": 6},
                {"name": f"Implement {feature}", "hours": 16},
                {"name": "Write unit tests", "hours": 8},
                {"name": "Create integration tests", "hours": 6},
                {"name": "Document feature", "hours": 4},
            ]
            feature_phase.acceptance_criteria = [
                f"{feature} works end-to-end",
                "All tests pass",
                "Feature documented",
                "No regression in existing features",
            ]
            phases.append(feature_phase)

        # Integration Phase
        integration = ProjectPhase(
            id=f"phase-{len(phases)}",
            name="Integration & Polish",
            type="testing",
            duration_weeks=2,
        )
        integration.dependencies = [phases[-1].id]
        integration.deliverables = [
            "End-to-end tests",
            "Performance benchmarks",
            "Security audit",
            "User documentation",
            "API documentation",
        ]
        integration.tasks = [
            {"name": "Create E2E tests", "hours": 12},
            {"name": "Performance testing", "hours": 8},
            {"name": "Security review", "hours": 8},
            {"name": "Write user docs", "hours": 8},
            {"name": "Polish UI/UX", "hours": 12},
        ]
        integration.acceptance_criteria = [
            "All features work together",
            "Performance meets requirements",
            "No critical security issues",
            "Documentation complete",
        ]
        phases.append(integration)

        # Deployment Phase
        deployment = ProjectPhase(
            id=f"phase-{len(phases)}",
            name="Deployment & Launch",
            type="deployment",
            duration_weeks=1,
        )
        deployment.dependencies = [phases[-1].id]
        deployment.deliverables = [
            "Production environment",
            "Monitoring setup",
            "Backup strategy",
            "Rollback plan",
            "Launch checklist",
        ]
        deployment.tasks = [
            {"name": "Setup production env", "hours": 8},
            {"name": "Configure monitoring", "hours": 6},
            {"name": "Implement backups", "hours": 4},
            {"name": "Create rollback plan", "hours": 4},
            {"name": "Launch preparation", "hours": 8},
        ]
        deployment.acceptance_criteria = [
            "Production environment stable",
            "Monitoring alerts configured",
            "Backups tested",
            "Team trained on operations",
        ]
        phases.append(deployment)

        return phases

    def generate_tech_stack_recommendations(self, project_info: Dict[str, Any]) -> List[TechStackDecision]:
        """Generate technology stack recommendations"""
        tech_stack = []

        # Analyze requirements to determine stack
        requirements = " ".join(project_info.get("requirements", []))
        features = " ".join(project_info.get("core_features", []))
        all_text = requirements.lower() + " " + features.lower()

        # Language decision
        language_decision = TechStackDecision(category="language", choice="", rationale="")

        if "real-time" in all_text or "websocket" in all_text:
            language_decision.choice = "Node.js/TypeScript"
            language_decision.rationale = "Excellent real-time support and unified language across stack"
            language_decision.alternatives_considered = [
                "Python + Django Channels",
                "Go",
                "Elixir",
            ]
        elif "machine learning" in all_text or "ai" in all_text or "data" in all_text:
            language_decision.choice = "Python"
            language_decision.rationale = "Rich ecosystem for ML/AI and data processing"
            language_decision.alternatives_considered = ["R", "Julia", "Java"]
        elif "mobile" in all_text:
            language_decision.choice = "React Native/TypeScript"
            language_decision.rationale = "Cross-platform mobile development with code reuse"
            language_decision.alternatives_considered = [
                "Flutter",
                "Native (Swift/Kotlin)",
                "Ionic",
            ]
        else:
            language_decision.choice = "Python"
            language_decision.rationale = "Rapid development, extensive libraries, strong community"
            language_decision.alternatives_considered = ["Node.js", "Ruby", "Go"]

        language_decision.constraints = [
            "Team expertise",
            "Ecosystem maturity",
            "Performance requirements",
        ]
        language_decision.risks = [
            "Learning curve for team members",
            "Potential performance bottlenecks",
        ]
        tech_stack.append(language_decision)

        # Framework decision
        framework_decision = TechStackDecision(category="framework", choice="", rationale="")

        if language_decision.choice == "Python":
            if "api" in all_text or "rest" in all_text:
                framework_decision.choice = "FastAPI"
                framework_decision.rationale = "Modern, fast, automatic documentation, async support"
                framework_decision.alternatives_considered = [
                    "Django REST",
                    "Flask",
                    "Falcon",
                ]
            else:
                framework_decision.choice = "Django"
                framework_decision.rationale = "Batteries included, rapid development, strong security"
                framework_decision.alternatives_considered = [
                    "Flask",
                    "FastAPI",
                    "Pyramid",
                ]
        elif "TypeScript" in language_decision.choice:
            framework_decision.choice = "NestJS"
            framework_decision.rationale = "Enterprise-grade, modular architecture, TypeScript-first"
            framework_decision.alternatives_considered = ["Express", "Fastify", "Koa"]

        framework_decision.constraints = [
            "Learning curve",
            "Community support",
            "Plugin ecosystem",
        ]
        framework_decision.risks = [
            "Framework limitations",
            "Version upgrade complexity",
        ]
        tech_stack.append(framework_decision)

        # Database decision
        db_decision = TechStackDecision(category="database", choice="", rationale="")

        if "graph" in all_text or "relationship" in all_text:
            db_decision.choice = "Neo4j"
            db_decision.rationale = "Optimized for relationship-heavy data"
            db_decision.alternatives_considered = [
                "PostgreSQL with graph extensions",
                "ArangoDB",
            ]
        elif "real-time" in all_text or "chat" in all_text:
            db_decision.choice = "PostgreSQL + Redis"
            db_decision.rationale = "PostgreSQL for persistence, Redis for real-time features"
            db_decision.alternatives_considered = ["MongoDB", "CassandraDB"]
        elif "analytics" in all_text or "reporting" in all_text:
            db_decision.choice = "PostgreSQL"
            db_decision.rationale = "Excellent analytical capabilities, window functions, extensions"
            db_decision.alternatives_considered = [
                "ClickHouse",
                "TimescaleDB",
                "Snowflake",
            ]
        else:
            db_decision.choice = "PostgreSQL"
            db_decision.rationale = "Reliable, feature-rich, excellent performance"
            db_decision.alternatives_considered = ["MySQL", "MongoDB", "SQLite"]

        db_decision.constraints = [
            "Data volume",
            "Query complexity",
            "Scaling requirements",
        ]
        db_decision.risks = ["Migration complexity", "Operational overhead"]
        tech_stack.append(db_decision)

        return tech_stack

    def generate_api_contracts(self, project_info: Dict[str, Any]) -> List[APIEndpoint]:
        """Generate API contract specifications"""
        endpoints = []

        # Extract entities from requirements
        entities = self._extract_entities(project_info.get("requirements", []))

        # Generate CRUD endpoints for each entity
        for entity in entities[:5]:  # Limit to 5 main entities
            entity_lower = entity.lower()
            entity_plural = entity_lower + "s"

            # GET all
            get_all = APIEndpoint(
                method="GET",
                path=f"/api/{entity_plural}",
                description=f"Retrieve all {entity_plural}",
            )
            get_all.auth_required = True
            get_all.rate_limit = "100 requests per minute"
            get_all.request_schema = {}
            get_all.response_schema = {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"$ref": f"#/definitions/{entity}"},
                    },
                    "total": {"type": "integer"},
                    "page": {"type": "integer"},
                    "limit": {"type": "integer"},
                },
            }
            get_all.errors = [
                {"code": 401, "message": "Unauthorized"},
                {"code": 429, "message": "Too many requests"},
            ]
            endpoints.append(get_all)

            # GET by ID
            get_one = APIEndpoint(
                method="GET",
                path=f"/api/{entity_plural}/{{id}}",
                description=f"Retrieve a specific {entity_lower}",
            )
            get_one.auth_required = True
            get_one.rate_limit = "100 requests per minute"
            get_one.request_schema = {}
            get_one.response_schema = {
                "type": "object",
                "properties": {"data": {"$ref": f"#/definitions/{entity}"}},
            }
            get_one.errors = [
                {"code": 401, "message": "Unauthorized"},
                {"code": 404, "message": f"{entity} not found"},
            ]
            endpoints.append(get_one)

            # POST create
            create = APIEndpoint(
                method="POST",
                path=f"/api/{entity_plural}",
                description=f"Create a new {entity_lower}",
            )
            create.auth_required = True
            create.rate_limit = "20 requests per minute"
            create.request_schema = {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
            }
            create.response_schema = {
                "type": "object",
                "properties": {
                    "data": {"$ref": f"#/definitions/{entity}"},
                    "message": {"type": "string"},
                },
            }
            create.errors = [
                {"code": 400, "message": "Invalid input"},
                {"code": 401, "message": "Unauthorized"},
                {"code": 409, "message": f"{entity} already exists"},
            ]
            endpoints.append(create)

            # PUT update
            update = APIEndpoint(
                method="PUT",
                path=f"/api/{entity_plural}/{{id}}",
                description=f"Update an existing {entity_lower}",
            )
            update.auth_required = True
            update.rate_limit = "50 requests per minute"
            update.request_schema = create.request_schema
            update.response_schema = create.response_schema
            update.errors = [
                {"code": 400, "message": "Invalid input"},
                {"code": 401, "message": "Unauthorized"},
                {"code": 404, "message": f"{entity} not found"},
            ]
            endpoints.append(update)

            # DELETE
            delete = APIEndpoint(
                method="DELETE",
                path=f"/api/{entity_plural}/{{id}}",
                description=f"Delete a {entity_lower}",
            )
            delete.auth_required = True
            delete.rate_limit = "20 requests per minute"
            delete.request_schema = {}
            delete.response_schema = {
                "type": "object",
                "properties": {"message": {"type": "string"}},
            }
            delete.errors = [
                {"code": 401, "message": "Unauthorized"},
                {"code": 404, "message": f"{entity} not found"},
            ]
            endpoints.append(delete)

        # Add authentication endpoints
        auth_endpoints = [
            APIEndpoint(
                method="POST",
                path="/api/auth/login",
                description="Authenticate user and receive token",
            ),
            APIEndpoint(
                method="POST",
                path="/api/auth/register",
                description="Register a new user account",
            ),
            APIEndpoint(
                method="POST",
                path="/api/auth/refresh",
                description="Refresh authentication token",
            ),
            APIEndpoint(
                method="POST",
                path="/api/auth/logout",
                description="Invalidate authentication token",
            ),
        ]

        for auth_ep in auth_endpoints:
            auth_ep.auth_required = False if "login" in auth_ep.path or "register" in auth_ep.path else True
            auth_ep.rate_limit = "10 requests per minute"
            auth_ep.request_schema = {
                "type": "object",
                "required": (["email", "password"] if "login" in auth_ep.path or "register" in auth_ep.path else []),
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string", "minLength": 8},
                },
            }
            auth_ep.response_schema = {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "user": {"$ref": "#/definitions/User"},
                },
            }
            auth_ep.errors = [
                {"code": 400, "message": "Invalid credentials"},
                {"code": 429, "message": "Too many attempts"},
            ]
            endpoints.append(auth_ep)

        return endpoints

    def _extract_entities(self, requirements: List[str]) -> List[str]:
        """Extract entity names from requirements"""
        entities = []
        common_entities = [
            "user",
            "users",
            "account",
            "profile",
            "product",
            "products",
            "item",
            "items",
            "order",
            "orders",
            "transaction",
            "transactions",
            "category",
            "categories",
            "tag",
            "tags",
            "post",
            "posts",
            "article",
            "articles",
            "comment",
            "comments",
            "review",
            "reviews",
            "message",
            "messages",
            "notification",
            "notifications",
            "project",
            "projects",
            "task",
            "tasks",
            "team",
            "teams",
            "organization",
            "organizations",
        ]

        requirements_text = " ".join(requirements).lower()

        for entity in common_entities:
            if entity in requirements_text:
                # Capitalize and singularize for consistency
                entity_name = entity.rstrip("s").capitalize()
                if entity_name not in entities:
                    entities.append(entity_name)

        # If no entities found, use defaults
        if not entities:
            entities = ["User", "Resource", "Setting"]

        return entities

    def generate_development_guidelines(self, tech_stack: List[TechStackDecision]) -> str:
        """Generate development guidelines based on tech stack"""

        # Find language and framework
        language = next((d.choice for d in tech_stack if d.category == "language"), "Python")
        framework = next((d.choice for d in tech_stack if d.category == "framework"), "")
        database = next((d.choice for d in tech_stack if d.category == "database"), "PostgreSQL")

        guidelines = f"""# Development Guidelines

## Technology Stack
- **Language**: {language}
- **Framework**: {framework}
- **Database**: {database}

## Project Structure

### Directory Layout
```
project-root/
├── src/                  # Source code
│   ├── api/             # API endpoints
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── utils/           # Utility functions
│   └── config/          # Configuration
├── tests/               # Test files
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/            # End-to-end tests
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── config/              # Configuration files
```

## Coding Standards

### General Principles
- **DRY** (Don't Repeat Yourself)
- **SOLID** principles
- **YAGNI** (You Aren't Gonna Need It)
- **KISS** (Keep It Simple, Stupid)

### Code Style
"""

        if "Python" in language:
            guidelines += """- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting
- Use pylint/flake8 for linting
"""
        elif "TypeScript" in language or "JavaScript" in language:
            guidelines += """- Use ESLint and Prettier
- Prefer const over let
- Use async/await over promises
- Use TypeScript strict mode
- Maximum line length: 100 characters
"""

        guidelines += f"""
### Naming Conventions
- **Classes**: PascalCase (e.g., UserAccount)
- **Functions/Methods**: {"snake_case" if "Python" in language else "camelCase"}
- **Constants**: UPPER_SNAKE_CASE
- **Files**: {"snake_case.py" if "Python" in language else "kebab-case.ts"}

## Development Workflow

### Git Workflow
1. Create feature branch from main
2. Make small, focused commits
3. Write descriptive commit messages
4. Create pull request with description
5. Ensure CI passes
6. Get code review
7. Squash and merge

### Commit Message Format
```
type(scope): subject

body (optional)

footer (optional)
```

Types: feat, fix, docs, style, refactor, test, chore

## Testing Requirements

### Test Coverage
- Minimum coverage: 80%
- Critical paths: 100%
- New features must include tests
- Bug fixes must include regression tests

### Test Types
1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete user workflows
4. **Performance Tests**: Test response times and load

## API Design Guidelines

### RESTful Principles
- Use appropriate HTTP methods
- Return appropriate status codes
- Version your API (/api/v1)
- Use consistent naming conventions

### Response Format
```json
{{
  "success": true,
  "data": {{}},
  "error": null,
  "metadata": {{
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }}
}}
```

## Security Guidelines

### General Security
- Never commit secrets
- Use environment variables
- Validate all inputs
- Sanitize all outputs
- Use HTTPS in production
- Implement rate limiting

### Authentication & Authorization
- Use JWT or session tokens
- Implement refresh tokens
- Hash passwords with bcrypt/argon2
- Implement RBAC (Role-Based Access Control)

## Database Guidelines

### Schema Design
- Normalize to 3NF minimum
- Use appropriate indexes
- Document relationships
- Use migrations for changes

### Query Optimization
- Avoid N+1 queries
- Use eager loading when appropriate
- Profile slow queries
- Use query builders/ORMs correctly

## Documentation Requirements

### Code Documentation
- Document all public APIs
- Include examples in docstrings
- Document complex algorithms
- Keep documentation up-to-date

### Project Documentation
- README with setup instructions
- API documentation (OpenAPI/Swagger)
- Architecture decisions (ADRs)
- Deployment guide

## Performance Guidelines

### Optimization Principles
- Measure before optimizing
- Optimize algorithms before code
- Cache expensive operations
- Use async/concurrent processing

### Monitoring
- Log important events
- Track response times
- Monitor error rates
- Set up alerts for anomalies

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Security scan complete
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Database migrations ready

### Deployment
- [ ] Backup database
- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Monitor error rates
- [ ] Have rollback plan ready

## Package Management

### Installation
```bash
{self._get_install_command(language)}
```

### Running the Project
```bash
{self._get_run_command(language, framework)}
```

---
*These guidelines are living documents. Update them as the project evolves.*
"""
        return guidelines

    def _get_package_manager(self, language: str) -> str:
        """Get package manager for language"""
        if "Python" in language:
            return "pip/poetry"
        elif "TypeScript" in language or "Node" in language:
            return "npm/yarn"
        elif "Ruby" in language:
            return "bundler"
        elif "Go" in language:
            return "go mod"
        return "package manager"

    def _get_install_command(self, language: str) -> str:
        """Get install command for language"""
        if "Python" in language:
            return "pip install -r requirements.txt"
        elif "TypeScript" in language or "Node" in language:
            return "npm install"
        elif "Ruby" in language:
            return "bundle install"
        elif "Go" in language:
            return "go mod download"
        return "install dependencies"

    def _get_run_command(self, language: str, framework: str) -> str:
        """Get run command for language/framework"""
        if "FastAPI" in framework:
            return "uvicorn main:app --reload"
        elif "Django" in framework:
            return "python manage.py runserver"
        elif "Flask" in framework:
            return "flask run"
        elif "NestJS" in framework:
            return "npm run start:dev"
        elif "Express" in framework:
            return "npm run dev"
        return "start application"

    def generate_full_specification(self, prd_path: Path) -> Dict[str, Any]:
        """Generate comprehensive project specification from PRD"""

        # Ingest PRD
        project_info = self.ingest_prd(prd_path)

        # Generate all specification components
        constitution = self.generate_project_constitution(project_info)
        phases = self.generate_phase_breakdown(project_info)
        tech_stack = self.generate_tech_stack_recommendations(project_info)
        api_endpoints = self.generate_api_contracts(project_info)
        guidelines = self.generate_development_guidelines(tech_stack)

        # Write specification files
        (self.specs_dir / "CONSTITUTION.md").write_text(constitution)
        (self.specs_dir / "PHASES.md").write_text(self.formatter.format_phases_document(phases))
        (self.specs_dir / "ADR-001-tech-stack.md").write_text(self.formatter.format_adr(tech_stack))
        (self.specs_dir / "API_CONTRACT.md").write_text(self.formatter.format_api_document(api_endpoints))
        (self.specs_dir / "DEVELOPMENT_GUIDELINES.md").write_text(guidelines)

        # Update PROJECT.md
        self.formatter.update_project_md(project_info, phases, tech_stack, api_endpoints)

        return {
            "project_info": project_info,
            "phases": phases,
            "tech_stack": tech_stack,
            "api_endpoints": api_endpoints,
            "specs_written": [
                "CONSTITUTION.md",
                "PHASES.md",
                "ADR-001-tech-stack.md",
                "API_CONTRACT.md",
                "DEVELOPMENT_GUIDELINES.md",
            ],
        }

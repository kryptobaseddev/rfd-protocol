# RFD Configuration Schema

## Overview
RFD uses `.rfd/config.yaml` for immutable project configuration and `.rfd/memory.db` for all dynamic state.

## Complete Schema Definition

```yaml
---
# Required Fields
name: string                    # Project name (required)
description: string              # Brief description (required, max 100 words)
version: string                  # Project version following semver (required)

# Technology Stack (required, but extensible)
stack:
  language: string               # Primary language (python, javascript, go, rust, etc.)
  framework: string              # Main framework (fastapi, express, rails, etc.)
  database: string               # Database type (sqlite, postgresql, mongodb, etc.)
  
  # Optional stack extensions
  runtime: string                # Runtime environment (node, deno, bun, python3.11)
  package_manager: string        # Package manager (npm, yarn, pnpm, pip, cargo)
  test_framework: string         # Testing framework (pytest, jest, mocha, etc.)
  build_tool: string             # Build tool (webpack, vite, make, cargo)
  deployment: string             # Deployment target (docker, kubernetes, vercel, etc.)
  ci_cd: string                  # CI/CD platform (github-actions, gitlab-ci, jenkins)
  monitoring: string             # Monitoring solution (datadog, newrelic, prometheus)
  
# Validation Rules (required)
rules:
  max_files: integer             # Maximum number of files allowed
  max_loc_per_file: integer      # Maximum lines per file
  must_pass_tests: boolean       # Whether tests must pass for checkpoint
  no_mocks_in_prod: boolean      # Prohibit mock data in production code
  
  # Optional validation rules
  min_test_coverage: integer     # Minimum test coverage percentage (0-100)
  max_complexity: integer        # Maximum cyclomatic complexity
  require_types: boolean         # Require type annotations/declarations
  require_docs: boolean          # Require documentation for public APIs
  max_dependencies: integer      # Maximum number of dependencies
  security_scan: boolean         # Run security scanning on checkpoints

# Constraints (optional but recommended)
constraints:
  - string                       # List of project constraints/rules

# API Contract (optional, for web services)
api_contract:
  base_url: string               # Base URL for API
  version: string                # API version
  auth_type: string              # none|basic|bearer|oauth2|api_key
  rate_limit: object             # Rate limiting rules
  health_check: string           # Health check endpoint path
  
  endpoints:
    - method: string             # HTTP method (GET, POST, PUT, DELETE, etc.)
      path: string               # Endpoint path
      description: string        # What this endpoint does
      auth_required: boolean     # Whether auth is required
      validates: string          # Validation/response format
      request_schema: object     # Request body schema (JSON Schema)
      response_schema: object    # Response schema (JSON Schema)
      errors: [object]           # Possible error responses

# Database Schema (optional)
database_schema:
  tables:
    - name: string               # Table name
      description: string        # Table purpose
      columns: [object]          # Column definitions
      indexes: [string]          # Index definitions
      relationships: [object]    # Foreign key relationships

# Environment Configuration (optional)
environments:
  development:
    variables: object            # Environment variables
    services: [string]           # Required services
    ports: [integer]             # Port mappings
  staging:
    variables: object
    services: [string]
    ports: [integer]
  production:
    variables: object
    services: [string]
    ports: [integer]

# Team Information (optional)
team:
  lead: string                   # Project lead
  developers: [string]           # Developer list
  reviewers: [string]            # Code reviewers
  stakeholders: [string]         # Project stakeholders

# All dynamic data (features, milestones, metrics) is stored in the database

# RFD Configuration (optional)
rfd_config:
  auto_validate: boolean         # Run validation on every checkpoint
  strict_mode: boolean           # Fail fast on any violation
  session_timeout: integer       # Session timeout in minutes
  checkpoint_frequency: string   # hourly|daily|on_commit|manual
  backup_enabled: boolean        # Enable checkpoint backups
  sync_enabled: boolean          # Enable cross-session sync
---

# Project Name

[Markdown content describing the project in detail]
```

## Field Descriptions

### Required Fields

#### `name`
- **Type**: string
- **Required**: Yes
- **Description**: The official name of your project
- **Example**: `"RFD Protocol"`

#### `description`
- **Type**: string
- **Required**: Yes
- **Description**: Brief description of what the project does (max 100 words)
- **Example**: `"Reality-First Development protocol that prevents AI hallucination"`

#### `version`
- **Type**: string
- **Required**: Yes
- **Description**: Project version following semantic versioning
- **Example**: `"1.0.0"`

### Stack Configuration

The `stack` section is required but highly extensible:

#### Core Stack Fields (Required)
- `language`: Primary programming language
- `framework`: Main application framework
- `database`: Database system

#### Extended Stack Fields (Optional)
- `runtime`: Specific runtime version
- `package_manager`: Package management tool
- `test_framework`: Testing framework
- `build_tool`: Build system
- `deployment`: Deployment platform
- `ci_cd`: CI/CD platform
- `monitoring`: Monitoring solution

### Validation Rules

#### Required Rules
- `max_files`: Maximum file count limit
- `max_loc_per_file`: Maximum lines per file
- `must_pass_tests`: Whether tests must pass
- `no_mocks_in_prod`: Prohibit mock data

#### Optional Rules
- `min_test_coverage`: Minimum coverage percentage
- `max_complexity`: Cyclomatic complexity limit
- `require_types`: Enforce type annotations
- `require_docs`: Enforce documentation
- `max_dependencies`: Dependency limit
- `security_scan`: Enable security scanning

### Dynamic Data (Database)

All features, milestones, and metrics are managed in the database:
- Use `rfd feature add` to add features
- Use `rfd feature list` to view features
- Use `rfd feature complete` to mark complete
- Use `rfd progress` to view metrics

## Configuration Management

### Static Configuration (.rfd/config.yaml)
Edit config.yaml for:
- Stack changes (requires reinit)
- Rule modifications
- Constraint updates

### Dynamic State (Database)
All dynamic data managed through commands:

```bash
# Feature management
rfd feature add <id> -d "description" -a "acceptance"
rfd feature list
rfd feature start <id>
rfd feature complete <id>

# Progress tracking
rfd checkpoint "message"
rfd progress
```

## Examples

### Minimal config.yaml
```yaml
project:
  name: "My API"
  description: "Simple REST API"
  version: "0.1.0"
  
stack:
  language: python
  framework: fastapi
  database: sqlite
  
rules:
  max_files: 50
  max_loc_per_file: 500
  must_pass_tests: true
  no_mocks_in_prod: true
```

### Full config.yaml Example
```yaml
---
name: "Enterprise Platform"
description: "Multi-tenant SaaS platform"
version: "2.1.0"
stack:
  language: typescript
  framework: nestjs
  database: postgresql
  runtime: node-20
  package_manager: pnpm
  test_framework: jest
  build_tool: webpack
  deployment: kubernetes
  ci_cd: github-actions
  monitoring: datadog
rules:
  max_files: 200
  max_loc_per_file: 500
  must_pass_tests: true
  no_mocks_in_prod: true
  min_test_coverage: 80
  max_complexity: 10
  require_types: true
  require_docs: true
  max_dependencies: 50
  security_scan: true
# Features stored in database, not config file
constraints:
  - "Must be GDPR compliant"
  - "Support 10,000 concurrent users"
  - "99.9% uptime SLA"
api_contract:
  base_url: "https://api.example.com"
  version: "v2"
  auth_type: bearer
  health_check: "/health"
  endpoints:
    - method: POST
      path: "/auth/signup"
      description: "Register new user"
      auth_required: false
      validates: "returns 201 with user object"
team:
  lead: "@alice"
  developers: ["@john", "@sarah", "@bob"]
  reviewers: ["@alice", "@charlie"]
milestones:
  - id: mvp
    name: "MVP Release"
    due_date: 2024-03-01
    features: ["user_auth", "billing"]
    status: active
---
```

## Schema Validation

RFD validates .rfd/config.yaml on:
- Every `rfd init`
- Every `rfd checkpoint`
- Every `rfd validate`
- Every `rfd audit`

Validation checks:
- Required fields present
- Field types correct
- Enum values valid
- Dependencies exist
- No circular dependencies
- Constraints logical

## Best Practices

1. **Start minimal**: Begin with required fields only
2. **Expand gradually**: Add optional fields as needed
3. **Keep it truthful**: Update status accurately
4. **Version properly**: Follow semantic versioning
5. **Document constraints**: Be explicit about limitations
6. **Track metrics**: Use RFD's automatic tracking

## Migration Guide

### From PROJECT.md to config.yaml (v5.0)
```bash
# Initialize with wizard
rfd init --wizard

# Validate new configuration
rfd spec validate
```

### Adding Custom Fields
RFD preserves unknown fields, allowing custom extensions:

```yaml
---
# Standard fields...

# Custom fields (preserved but not validated)
custom:
  client_name: "Acme Corp"
  contract_value: 100000
  internal_code: "PROJ-123"
---
```
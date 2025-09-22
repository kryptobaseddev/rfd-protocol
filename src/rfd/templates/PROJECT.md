---
version: "1.0"
name: "{project_name}"
description: "{project_description}"
stack:
  language: "{language}"
  framework: "{framework}"
  database: "{database}"
rules:
  max_files: {max_files}
  max_loc_per_file: {max_loc}
  must_pass_tests: true
  no_mocks_in_prod: true
features:
{features}
constraints:
{constraints}
{api_contract}
---

# {project_name}

{project_description}

## Technology Stack

- **Language**: {language}
- **Framework**: {framework}
- **Database**: {database}

## Features

{features_detail}

## Development Rules

- Maximum {max_files} files allowed
- Maximum {max_loc} lines per file
- All tests must pass before commit
- No mock data in production code

## Getting Started

1. Initialize RFD: `rfd init`
2. Start development: `rfd session start <feature_id>`
3. Build and validate: `rfd build && rfd validate`
4. Save checkpoint: `rfd checkpoint "message"`

## RFD Commands

```bash
rfd check          # Quick status check
rfd build          # Build current feature
rfd validate       # Run validation tests
rfd checkpoint     # Save working state
rfd revert         # Return to last working state
rfd session start  # Begin new feature
```

## Constraints

{constraints_detail}

---

Generated with RFD Protocol v1.0
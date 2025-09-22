# PROJECT.md Template

**Project Name**: [Enter your project name]
**Description**: [Brief description of what this project does]
**Stack**: [Technology stack being used]

## Features

Each feature should have clear acceptance criteria and be testable.

### Feature 1: [Feature Name]
- **ID**: feature_1
- **Description**: [What this feature does]
- **Status**: pending | in_progress | complete
- **Acceptance Criteria**:
  - [ ] Criterion 1: [Specific, testable requirement]
  - [ ] Criterion 2: [Another specific requirement]
  - [ ] Criterion 3: [Yet another requirement]

### Feature 2: [Feature Name]
- **ID**: feature_2
- **Description**: [What this feature does]
- **Status**: pending | in_progress | complete
- **Acceptance Criteria**:
  - [ ] Criterion 1: [Specific, testable requirement]
  - [ ] Criterion 2: [Another specific requirement]

## API Contract (Optional)

If your project has an API, define the contract here:

```yaml
base_url: "http://localhost:8000"
health_check: "/health"
endpoints:
  - path: "/api/endpoint1"
    method: "GET"
    validates: "returns 200 {data: string}"
  - path: "/api/endpoint2"
    method: "POST"
    validates: "returns 201 {id: number, status: string}"
```

## Rules (Optional)

Define any development rules or constraints:

```yaml
max_files: 10
max_loc_per_file: 200
```

## Architecture Notes

[Any important architectural decisions or constraints]

## Reality Checkpoints

- [ ] All specified files exist
- [ ] All specified functions/classes exist
- [ ] All tests pass
- [ ] API endpoints respond correctly
- [ ] Integration between components works
- [ ] Real data flows through the system

---

**Instructions**: 
1. Replace all `[bracketed placeholders]` with actual values
2. Define concrete, testable acceptance criteria for each feature
3. Keep features small and focused
4. Update status as you progress
5. Use RFD validation to ensure reality matches this spec
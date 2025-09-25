# RFD Database-First Architecture

## Current Problems (What's Wrong)

### Mixed State Management
- PROJECT.md contains BOTH static config AND dynamic state (features with status)
- PROGRESS.md duplicates what should be in the checkpoints table
- Constant "syncing" between markdown files and database
- Multiple sources of truth = guaranteed inconsistency

### Not Actually Dogfooding
- If RFD is about "Reality-First Development", the reality should be in the database
- Markdown files for state management is NOT scalable
- We're building a database-driven tool but not using the database!

## Proper Architecture (What's Right)

### 1. Immutable Project Configuration
**File**: `.rfd/config.yaml` (created during `rfd init`)
```yaml
# IMMUTABLE after init - like a constitution for the project
project:
  name: "RFD Protocol"
  description: "Reality-First Development Protocol"
  version: "1.0.0"  # Project version, not RFD version

stack:
  language: python
  framework: click
  database: sqlite
  
rules:
  max_files: 50
  max_loc_per_file: 1200
  must_pass_tests: true
  no_mocks_in_prod: true

constraints:
  - "NO new features until 100% tests pass"
  - "MUST use RFD workflow for all fixes"
  - "MUST validate each fix with tests"
```

### 2. Database Schema (All Dynamic State)

```sql
-- Project metadata (mutable)
CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    current_version TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Features (all feature management)
CREATE TABLE features (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    acceptance_criteria TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending|building|testing|complete|blocked
    priority INTEGER DEFAULT 0,
    assigned_to TEXT,
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    estimated_hours REAL,
    actual_hours REAL,
    metadata JSON
);

-- Dependencies between features
CREATE TABLE feature_dependencies (
    feature_id TEXT,
    depends_on TEXT,
    FOREIGN KEY (feature_id) REFERENCES features(id),
    FOREIGN KEY (depends_on) REFERENCES features(id)
);

-- Checkpoints (build history)
CREATE TABLE checkpoints (
    id INTEGER PRIMARY KEY,
    feature_id TEXT,
    timestamp TEXT,
    message TEXT,
    validation_passed BOOLEAN,
    build_passed BOOLEAN,
    tests_passed BOOLEAN,
    git_hash TEXT,
    evidence JSON,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);

-- Sessions (work sessions)
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    feature_id TEXT,
    started_at TEXT,
    ended_at TEXT,
    success BOOLEAN,
    context JSON,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);

-- Tasks (granular work items)
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    feature_id TEXT,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);

-- Phases (project phases)
CREATE TABLE phases (
    id TEXT PRIMARY KEY,
    name TEXT,
    sequence INTEGER,
    status TEXT DEFAULT 'pending',
    started_at TEXT,
    completed_at TEXT
);

-- Metrics (auto-tracked)
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    metric_name TEXT,
    value REAL,
    context JSON
);
```

### 3. CLI Commands (Database-First)

```bash
# Initialize project (creates .rfd/ with config.yaml and database)
rfd init --name "My Project" --stack python/fastapi/postgres

# Feature management (all database operations)
rfd feature add "user_auth" --description "User authentication" --acceptance "Users can login"
rfd feature list
rfd feature status user_auth
rfd feature start user_auth
rfd feature complete user_auth

# No more "spec add" - features ARE the spec
rfd feature show  # Shows all features (the dynamic spec)

# Progress tracking (from database)
rfd progress  # Shows checkpoints from database
rfd checkpoint "Fixed login bug"  # Adds to database

# Session management (database-driven)
rfd session start user_auth
rfd session status
rfd session end

# Analysis (queries database)
rfd analyze  # Analyzes database state
rfd status   # Shows database state
rfd dashboard  # Visualizes database state
```

### 4. No More Markdown State Files

**DELETE**:
- PROJECT.md (for state - can keep for documentation)
- PROGRESS.md (completely redundant)

**REPORTS** (generated from database):
- `rfd report` - Generates a markdown report from database
- `rfd export` - Exports current state as markdown
- These are OUTPUT, not state storage

### 5. File Structure

```
my-project/
├── .rfd/
│   ├── config.yaml          # Immutable project config
│   ├── memory.db            # ALL dynamic state
│   ├── context/            
│   │   ├── current.json     # Current session context
│   │   └── memory.json      # AI memory
│   └── cache/               # Temporary files
├── src/                     # Your actual code
├── tests/                   # Your tests
└── README.md               # Documentation (not state!)
```

## Migration Path

1. **Phase 1**: Stop writing to PROJECT.md and PROGRESS.md
   - Make all writes go to database
   - Keep reads for backward compatibility

2. **Phase 2**: Migrate existing data
   - Parse PROJECT.md features into database
   - Parse PROGRESS.md into checkpoints table
   - Create config.yaml from PROJECT.md static parts

3. **Phase 3**: Remove markdown dependencies
   - Update all commands to read from database
   - Remove sync code
   - Delete PROJECT.md and PROGRESS.md

4. **Phase 4**: True dogfooding
   - RFD manages RFD using only its database
   - No special files needed

## Benefits

1. **Single Source of Truth**: Database only
2. **Scalable**: Can handle thousands of features/checkpoints
3. **Queryable**: SQL for complex analysis
4. **Atomic**: Transactions ensure consistency
5. **Performance**: No file parsing needed
6. **True Dogfooding**: RFD uses RFD properly

## Example Usage

```bash
# Start a new project
$ rfd init --wizard
? Project name: my-api
? Language: python
? Framework: fastapi
? Database: postgresql
✅ Created .rfd/config.yaml (immutable)
✅ Created .rfd/memory.db (all state here)

# Add features
$ rfd feature add auth --description "User authentication" 
✅ Added feature 'auth' to database

$ rfd feature add billing --description "Payment processing" --depends-on auth
✅ Added feature 'billing' with dependency on 'auth'

# Work on features
$ rfd session start auth
✅ Started session for 'auth'

$ rfd checkpoint "Added login endpoint"
✅ Checkpoint saved to database

$ rfd feature complete auth
✅ Feature 'auth' marked complete in database

# Check progress (from database)
$ rfd progress
📊 Project Progress (from database):
  ✅ auth: Complete (3 checkpoints)
  ⏳ billing: Pending (0 checkpoints)

# Generate report (from database)
$ rfd report > status.md
✅ Generated status.md from database state
```

This is TRUE dogfooding - using the database as the single source of truth!
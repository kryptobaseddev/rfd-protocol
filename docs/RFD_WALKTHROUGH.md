# RFD Walkthrough - Complete Step-by-Step Guide

This walkthrough demonstrates RFD from installation to shipping your first feature. Follow along to understand how RFD prevents AI hallucination and ensures real code delivery.

## Table of Contents
1. [Installation & Verification](#installation--verification)
2. [Project Initialization](#project-initialization)
3. [Understanding PROJECT.md](#understanding-projectmd)
4. [Starting Your First Feature](#starting-your-first-feature)
5. [The Build-Validate-Checkpoint Cycle](#the-build-validate-checkpoint-cycle)
6. [Working with AI Tools](#working-with-ai-tools)
7. [Advanced Workflows](#advanced-workflows)
8. [Troubleshooting Guide](#troubleshooting-guide)

## Installation & Verification

### Step 1: Install RFD

```bash
# Install globally (recommended)
pip install rfd-protocol

# Or use pipx for isolated environment
pipx install rfd-protocol
```

### Step 2: Verify Installation

```bash
# Check version
rfd --version
# Expected: rfd, version X.X.X

# Check available commands
rfd --help
# Shows all available commands
```

If `rfd` command not found:
```bash
# Add to PATH
export PATH="$PATH:$HOME/.local/bin"

# Or use python module directly
python -m rfd.cli --version
```

## Project Initialization

### Option A: New Project with Interactive Wizard

```bash
# Create project directory
mkdir my-awesome-api
cd my-awesome-api

# Start interactive wizard
rfd init --wizard
```

The wizard will guide you through:

1. **Project Name**: `My Awesome API`
2. **Description**: `RESTful API for user management`
3. **Language Selection**: 
   ```
   Select language:
   1. Python
   2. JavaScript
   3. TypeScript
   4. Go
   > 1
   ```
4. **Framework Selection**:
   ```
   Select framework:
   1. FastAPI
   2. Flask
   3. Django
   > 1
   ```
5. **Database Selection**:
   ```
   Select database:
   1. SQLite
   2. PostgreSQL
   3. MySQL
   > 1
   ```
6. **First Feature Definition**:
   ```
   Feature ID: user_registration
   Description: User signup and login system
   Acceptance Criteria: Users can register with email and login
   ```

### Option B: Initialize from Requirements Document

```bash
# If you have a PRD or requirements document
rfd init --from-prd requirements.md
```

RFD will parse your document and generate:
- Feature breakdown
- Acceptance criteria
- Technology recommendations

### Option C: Quick Init for Existing Projects

```bash
# For existing codebases
cd existing-project/
rfd init --mode brownfield

# RFD analyzes your code and suggests:
# - Detected language: Python
# - Detected framework: FastAPI
# - Found 3 potential features
```

### What Gets Created

After initialization, you'll have:

```
your-project/
├── PROJECT.md       # Your project specification
├── CLAUDE.md        # AI assistant configuration
├── PROGRESS.md      # Progress tracking log
└── .rfd/           # RFD system directory
    ├── memory.db    # SQLite database (WAL mode)
    └── context/     # Session context
        └── memory.json
```

## Understanding PROJECT.md

PROJECT.md is your single source of truth. Let's examine a real example:

```yaml
---
name: "User Management API"
description: "RESTful API for user registration and authentication"
version: "1.0.0"

stack:
  language: python
  framework: fastapi
  database: sqlite
  
rules:
  max_files: 20           # Keep it simple
  max_loc_per_file: 300   # Enforce modularity
  must_pass_tests: true   # Tests are mandatory
  no_mocks_in_prod: true  # Real implementations only

features:
  - id: user_registration
    description: "User signup system"
    acceptance: "Users can register with email/password"
    status: pending
    
  - id: user_login
    description: "Authentication system"
    acceptance: "Users can login and receive JWT token"
    status: pending
    depends_on: [user_registration]

constraints:
  - "Passwords must be hashed with bcrypt"
  - "Email validation required"
  - "JWT tokens expire after 24 hours"
---

# User Management API

This API provides secure user registration and authentication...
```

### Key Points:
- **Features are locked**: You can't work on undefined features
- **Acceptance criteria are contracts**: They must be provably met
- **Dependencies are enforced**: Can't start user_login before user_registration
- **Rules are validated**: Every checkpoint must pass these rules

## Starting Your First Feature

### Step 1: Check Project Status

```bash
rfd check
```

Output:
```
=== RFD Status Check ===

📋 Validation: ❌ (no features built yet)
🔨 Build: ❌ (no code yet)
📝 Session: None active

📦 Features:
  ⏳ user_registration (0 checkpoints)
  ⏳ user_login (0 checkpoints) [blocked by: user_registration]

→ Next: rfd session start user_registration
```

### Step 2: Start Feature Session

```bash
rfd session start user_registration
```

Output:
```
✅ Started session for feature: user_registration

📋 Feature: User signup system
✅ Acceptance: Users can register with email/password
📁 Context saved to: .rfd/context/current.md

→ Next: Write code, then run 'rfd build'
```

### Step 3: Check Current Context

```bash
cat .rfd/context/current.md
```

Shows:
```markdown
---
session_id: 1
feature: user_registration
started: 2024-01-15T10:30:00
status: building
---

# Current Session: user_registration

## Feature Specification
User signup system

**Acceptance Criteria:**
Users can register with email/password

## Required Actions
1. Create User model
2. Add registration endpoint
3. Implement password hashing
4. Add email validation
5. Write tests
```

## The Build-Validate-Checkpoint Cycle

This is the core RFD loop that ensures reality:

### Step 1: Write Real Code

Create `main.py`:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import sqlite3

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: EmailStr
    password: str

@app.post("/register")
async def register(user: UserCreate):
    # Hash password
    hashed = pwd_context.hash(user.password)
    
    # Save to database
    conn = sqlite3.connect(".rfd/users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT
        )
    """)
    
    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (user.email, hashed)
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()
```

### Step 2: Build

```bash
rfd build
```

RFD automatically:
- Installs dependencies (fastapi, passlib, etc.)
- Starts the server
- Verifies it runs

Output:
```
🔨 Build Process
━━━━━━━━━━━━━━━━━━━━
Installing dependencies...
✅ fastapi installed
✅ passlib[bcrypt] installed
✅ email-validator installed

Starting server...
✅ Server running on http://127.0.0.1:8000

Build: ✅ PASSING
```

### Step 3: Validate

```bash
rfd validate
```

RFD checks:
- Does the registration endpoint exist?
- Can users actually register?
- Is password hashing implemented?
- Does the database work?

Output:
```
=== Validation Report ===

✅ max_files: 1 file (max: 20)
✅ max_loc_per_file: 45 lines (max: 300)
✅ no_mocks_in_prod: No mock data found
✅ feature_user_registration: 
   - POST /register endpoint found
   - Password hashing implemented
   - Database table created
   - Email validation active

Overall: ✅ PASSING
```

### Step 4: Checkpoint

Only when validation passes:

```bash
rfd checkpoint "Implemented user registration with bcrypt hashing"
```

Output:
```
✅ Checkpoint saved
Git commit: abc123
Timestamp: 2024-01-15T11:45:00
Feature progress: 100%
```

### Step 5: End Session

```bash
rfd session end
```

Output:
```
✅ Feature completed: user_registration
Duration: 1 hour 15 minutes
Checkpoints: 1
Status updated in PROJECT.md

→ Next feature available: user_login
```

## Working with AI Tools

### With Claude Code

Tell Claude:
```
Continue the RFD project. Work on the next feature.
```

Claude will automatically:
```bash
# 1. Check status
rfd check
> Next feature: user_login

# 2. Start session
rfd session start user_login

# 3. Read context
cat .rfd/context/current.md

# 4. Write code
# [implements login endpoint]

# 5. Validate
rfd build && rfd validate

# 6. Checkpoint if passing
rfd checkpoint "Added JWT login"
```

### Preventing Hallucination

Watch RFD catch AI mistakes:

```bash
# AI claims: "I implemented the complete authentication system"
rfd validate

❌ Validation Failed:
  - No /login endpoint found
  - No JWT generation code
  - No token validation
  - Tests failing: 0 of 3 passing

# AI cannot fake progress:
rfd checkpoint "Completed auth"
❌ Cannot checkpoint - validation failing
```

### Session Recovery

After restart:
```bash
# New session, who dis?
rfd check

📝 Session: user_login (started 2 hours ago)
   Last checkpoint: "Created login endpoint structure"
   Next: Implement JWT token generation
   
# Continue exactly where you left off
```

## Advanced Workflows

### Spec-Kit Style Development

```bash
# 1. Define immutable principles
rfd speckit constitution

# 2. Create detailed specifications  
rfd speckit specify

# 3. Identify ambiguities
rfd speckit clarify
> Q: Token expiration time?
> A: 24 hours

# 4. Generate implementation plan
rfd speckit plan
> Phase 1: Database schema
> Phase 2: API endpoints
> Phase 3: Authentication

# 5. Break into tasks
rfd speckit tasks
> Task 1: Create User model [can_parallel: false]
> Task 2: Add /register endpoint [can_parallel: false]  
> Task 3: Add /login endpoint [depends_on: 2]
> Task 4: Write tests [can_parallel: true]
```

### Cross-Artifact Analysis

```bash
rfd analyze
```

Output:
```
CROSS-ARTIFACT ANALYSIS REPORT
════════════════════════════════════

📋 SPEC ALIGNMENT
  ✅ All 2 features aligned with specification

📝 TASK CONSISTENCY
  ✅ All tasks match feature status
  
🔌 API IMPLEMENTATION
  Coverage: 100%
  ✅ POST /register - implemented
  ✅ POST /login - implemented

🧪 TEST COVERAGE
  Coverage: 95%
  ✅ Registration tests passing
  ✅ Login tests passing
  ⚠️ Edge case tests needed

📜 CONSTITUTION ADHERENCE
  ✅ No mock data in production
  ✅ All passwords hashed
  ✅ Email validation enforced

🛡️ INTEGRITY CHECK
  Hallucinations detected: 0
  Drift incidents: 0
  
Overall Health: EXCELLENT
```

### Reverting Changes

When things go wrong:

```bash
# Check recent checkpoints
rfd revert --list

# Revert to specific checkpoint
rfd revert --to "Before JWT implementation"

# Or just last checkpoint
rfd revert
```

## Troubleshooting Guide

### Common Issues and Solutions

#### "Command not found: rfd"
```bash
# Solution 1: Add to PATH
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc

# Solution 2: Use python module
python -m rfd.cli init
```

#### "No feature specified in PROJECT.md"
```bash
# Edit PROJECT.md and add feature
nano PROJECT.md

# Or use spec command
rfd spec add-feature
```

#### "Validation keeps failing"
```bash
# Get detailed error info
rfd validate --verbose

# Check specific feature
rfd validate --feature user_registration

# Debug mode
export RFD_DEBUG=1
rfd validate
```

#### "Lost session context"
```bash
# Recover from memory
rfd memory show

# Check last session
cat .rfd/context/current.md

# Force new session
rfd session start user_login --force
```

#### "Database locked"
```bash
# RFD uses WAL mode, but if issues:
rm .rfd/memory.db-wal
rm .rfd/memory.db-shm
rfd check
```

### Getting Help

```bash
# Built-in help
rfd --help
rfd session --help

# Check documentation
ls docs/

# Debug information
rfd debug --system-info
```

## Best Practices

### 1. Start Small
- Define minimal features first
- Get one feature fully working before moving on
- Use checkpoints frequently

### 2. Write Real Tests
```python
def test_user_registration():
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 200
    
    # Verify user actually exists in database
    conn = sqlite3.connect(".rfd/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", ("test@example.com",))
    assert cursor.fetchone() is not None
```

### 3. Use Meaningful Checkpoints
```bash
# Good
rfd checkpoint "Added user registration with email validation and bcrypt"

# Bad  
rfd checkpoint "Did stuff"
```

### 4. Keep Features Focused
- One feature = one clear capability
- Clear acceptance criteria
- Measurable success

### 5. Leverage Session Persistence
- RFD remembers everything
- Use `rfd memory show` to review context
- Trust the system to maintain state

## Complete Example Project

Let's build a minimal but complete project:

```bash
# 1. Setup
mkdir todo-api && cd todo-api
rfd init --wizard
# Choose: Python, FastAPI, SQLite

# 2. Define features in PROJECT.md
features:
  - id: create_todo
    acceptance: "POST /todos creates a todo"
  - id: list_todos  
    acceptance: "GET /todos returns all todos"

# 3. Implement first feature
rfd session start create_todo

# Write main.py
cat > main.py << 'EOF'
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class TodoCreate(BaseModel):
    title: str
    
@app.post("/todos")
async def create_todo(todo: TodoCreate):
    conn = sqlite3.connect("todos.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY,
            title TEXT
        )
    """)
    cursor.execute("INSERT INTO todos (title) VALUES (?)", (todo.title,))
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    return {"id": todo_id, "title": todo.title}
EOF

# 4. Build and validate
rfd build
rfd validate

# 5. Checkpoint
rfd checkpoint "Implemented create_todo endpoint"

# 6. Complete feature
rfd session end

# 7. Move to next feature
rfd session start list_todos

# ... continue development ...
```

## Summary

RFD ensures that:
1. **Every line of code is real** - No hallucinations
2. **Context persists perfectly** - Never lose your place
3. **Features are completed fully** - No partial implementations
4. **Progress is always valid** - Can't checkpoint broken code
5. **Development stays focused** - Can't drift from specifications

This walkthrough covered the essential workflow. For more advanced topics, see:
- [CLI Reference](CLI_REFERENCE.md) - All commands in detail
- [PROJECT.md Schema](PROJECT_SCHEMA.md) - Full configuration options
- [Claude Integration Guide](CLAUDE_CODE_GUIDE.md) - AI tool specifics

---

**Remember**: RFD is about reality first. If it doesn't run, it doesn't count.
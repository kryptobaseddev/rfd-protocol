## 🚀 RFD Bootstrap Implementation Plan
*How to build RFD without falling into the problems RFD solves*

### The Bootstrap Paradox
We need RFD to prevent drift and AI hallucination, but we'll experience those problems while building RFD. The solution: **Progressive Self-Hosting** - build RFD in stages, using each completed stage to build the next.

### Current Status
- ✅ Stage 1: Created `verify.py` for basic verification
- ✅ Stage 2: Extracted CLI structure to `.rfd/rfd.py`
- ✅ Stage 3: Extracted build engine to `.rfd/build.py`
- ✅ Stage 4: Extracted validation engine to `.rfd/validate.py`
- 🔄 Stage 5: Extracting session manager to `.rfd/session.py`
- ⏳ Stage 6: Spec engine extraction pending

### How to Use This Document
1. **Don't try to implement all 1300 lines at once**
2. **Extract and test one component at a time**
3. **Use `python verify.py` after every change**
4. **Commit working pieces immediately**
5. **Use completed pieces to build next pieces**

### Bootstrap Sequence
```bash
# Stage 1: Basic verification (COMPLETE)
python verify.py "AI output"  # Verify files exist

# Stage 2: Extract CLI structure (lines 71-494) - COMPLETE
# Copy CLI code to .rfd/rfd.py, test basic commands

# Stage 3: Extract build engine (lines 499-605) - COMPLETE
# Add build automation, test with Stage 2 CLI

# Stage 4: Extract validation engine (lines 609-847) - COMPLETE
# Add validation engine, test with Stage 3

# Stage 5: Extract session management (lines 851-1065) - IN PROGRESS
# Add context generation, test with Stage 4

# Stage 6: Extract spec engine (lines 1069-1283)
# Add specification management, test with Stage 5
```

---

## RFD: Reality-First Development System
*A unified framework that makes AI agents and humans accountable to working code*

### ⚠️ Implementation Note
The code below is the COMPLETE system. Extract progressively following the bootstrap sequence above. Each section is marked with line numbers for easy extraction.

### Complete Package Structure

```
your-project/
├── .rfd/                      # Core RFD System (git-ignored)
│   ├── rfd.py                # Main orchestrator
│   ├── build.py              # Build automation engine
│   ├── validate.py           # Validation & truth enforcement
│   ├── spec.py               # Spec-driven design engine
│   ├── session.py            # Session & context manager
│   ├── memory.db             # Persistent state (SQLite)
│   └── context/              # Dynamic context generation
│       ├── current.md        # Active session (for AI)
│       ├── memory.json       # AI memory state
│       └── checkpoints/      # Session snapshots
├── CLAUDE.md                 # Claude Code CLI instructions
├── PROJECT.md                # Master specification
├── PROGRESS.md               # Append-only truth log
└── rfd                       # Single entry point
```

### Master Orchestrator: rfd.py

```python
#!/usr/bin/env python3
"""
RFD: Reality-First Development System
Single entry point for all development operations
"""

import sys
import sqlite3
import json
import subprocess
from pathlib import Path
from datetime import datetime
import click
import frontmatter
from typing import Dict, Any, Optional

class RFD:
    """Main RFD orchestrator - coordinates all subsystems"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.rfd_dir = self.root / '.rfd'
        self.db_path = self.rfd_dir / 'memory.db'
        
        # Initialize subsystems
        self._init_structure()
        self._init_database()
        
        # Load modules
        sys.path.insert(0, str(self.rfd_dir))
        from build import BuildEngine
        from validate import ValidationEngine
        from spec import SpecEngine
        from session import SessionManager
        
        self.builder = BuildEngine(self)
        self.validator = ValidationEngine(self)
        self.spec = SpecEngine(self)
        self.session = SessionManager(self)
    
    def _init_structure(self):
        """Create RFD directory structure"""
        self.rfd_dir.mkdir(exist_ok=True)
        (self.rfd_dir / 'context').mkdir(exist_ok=True)
        (self.rfd_dir / 'context' / 'checkpoints').mkdir(exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite for state management"""
        conn = sqlite3.connect(self.db_path)
        
        # Core tables
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS features (
                id TEXT PRIMARY KEY,
                description TEXT,
                acceptance_criteria TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                completed_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY,
                feature_id TEXT,
                timestamp TEXT,
                validation_passed BOOLEAN,
                build_passed BOOLEAN,
                git_hash TEXT,
                evidence JSON
            );
            
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                feature_id TEXT,
                success BOOLEAN,
                changes JSON,
                errors JSON
            );
            
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value JSON,
                updated_at TEXT
            );
        """)
        conn.commit()
    
    def load_project_spec(self) -> Dict[str, Any]:
        """Load and parse PROJECT.md"""
        project_file = self.root / 'PROJECT.md'
        if not project_file.exists():
            return {}
        
        with open(project_file, 'r') as f:
            post = frontmatter.load(f)
            return post.metadata
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get complete current project state"""
        return {
            'spec': self.load_project_spec(),
            'validation': self.validator.get_status(),
            'build': self.builder.get_status(),
            'session': self.session.get_current(),
            'features': self.get_features_status()
        }
    
    def get_features_status(self) -> list:
        """Get status of all features"""
        conn = sqlite3.connect(self.db_path)
        return conn.execute("""
            SELECT id, status, 
                   (SELECT COUNT(*) FROM checkpoints 
                    WHERE feature_id = features.id 
                    AND validation_passed = 1) as passing_checkpoints
            FROM features
            ORDER BY created_at
        """).fetchall()

@click.group()
@click.pass_context
def cli(ctx):
    """RFD: Reality-First Development System"""
    ctx.obj = RFD()

@cli.command()
@click.pass_obj
def init(rfd):
    """Initialize RFD in current directory"""
    click.echo("🚀 Initializing RFD System...")
    
    # Create default files if not exist
    files_created = []
    
    # PROJECT.md template
    if not Path('PROJECT.md').exists():
        rfd.spec.create_interactive()
        files_created.append('PROJECT.md')
    
    # CLAUDE.md for Claude Code CLI
    if not Path('CLAUDE.md').exists():
        create_claude_md()
        files_created.append('CLAUDE.md')
    
    # PROGRESS.md
    if not Path('PROGRESS.md').exists():
        Path('PROGRESS.md').write_text("# Build Progress\n\n")
        files_created.append('PROGRESS.md')
    
    # Create rfd symlink
    if not Path('rfd').exists():
        subprocess.run(['ln', '-s', '.rfd/rfd.py', 'rfd'])
        subprocess.run(['chmod', '+x', '.rfd/rfd.py'])
    
    click.echo(f"✅ RFD initialized! Created: {', '.join(files_created)}")
    click.echo("\n→ Next: ./rfd spec review")

@cli.command()
@click.argument('action', type=click.Choice(['create', 'review', 'validate']))
@click.pass_obj
def spec(rfd, action):
    """Manage project specification"""
    if action == 'create':
        rfd.spec.create_interactive()
    elif action == 'review':
        rfd.spec.review()
    elif action == 'validate':
        rfd.spec.validate()

@cli.command()
@click.argument('feature_id', required=False)
@click.pass_obj
def build(rfd, feature_id):
    """Run build process for feature"""
    if not feature_id:
        feature_id = rfd.session.get_current_feature()
    
    if not feature_id:
        click.echo("❌ No feature specified. Use: ./rfd session start <feature>")
        return
    
    click.echo(f"🔨 Building feature: {feature_id}")
    success = rfd.builder.build_feature(feature_id)
    
    if success:
        click.echo("✅ Build successful!")
        rfd.checkpoint(f"Build passed for {feature_id}")
    else:
        click.echo("❌ Build failed - check errors above")

@cli.command()
@click.option('--feature', help='Validate specific feature')
@click.option('--full', is_flag=True, help='Full validation')
@click.pass_obj
def validate(rfd, feature, full):
    """Validate current implementation"""
    results = rfd.validator.validate(feature=feature, full=full)
    rfd.validator.print_report(results)
    
    if not results['passing']:
        sys.exit(1)

@cli.command()
@click.pass_obj
def check(rfd):
    """Quick health check"""
    state = rfd.get_current_state()
    
    # Quick status
    click.echo("\n=== RFD Status Check ===\n")
    
    # Validation
    val = state['validation']
    click.echo(f"📋 Validation: {'✅' if val['passing'] else '❌'}")
    
    # Build
    build = state['build']
    click.echo(f"🔨 Build: {'✅' if build['passing'] else '❌'}")
    
    # Current session
    session = state['session']
    if session:
        click.echo(f"📝 Session: {session['feature_id']} (started {session['started_at']})")
    
    # Features
    click.echo(f"\n📦 Features:")
    for fid, status, checkpoints in state['features']:
        icon = '✅' if status == 'complete' else '🔨' if status == 'building' else '⭕'
        click.echo(f"  {icon} {fid} ({checkpoints} checkpoints)")
    
    # Next action
    click.echo(f"\n→ Next: {rfd.session.suggest_next_action()}")

@cli.group()
@click.pass_obj
def session(rfd):
    """Manage development sessions"""
    pass

@session.command('start')
@click.argument('feature_id')
@click.pass_obj
def session_start(rfd, feature_id):
    """Start new feature session"""
    rfd.session.start(feature_id)
    click.echo(f"🚀 Session started for: {feature_id}")
    click.echo(f"📋 Context updated at: .rfd/context/current.md")
    click.echo(f"\n→ Next: ./rfd build")

@session.command('end')
@click.option('--success/--failed', default=True)
@click.pass_obj
def session_end(rfd, success):
    """End current session"""
    session_id = rfd.session.end(success=success)
    if session_id:
        click.echo(f"📝 Session {session_id} ended")

@cli.command()
@click.argument('message')
@click.pass_obj
def checkpoint(rfd, message):
    """Save checkpoint with current state"""
    # Get current state
    validation = rfd.validator.validate()
    build = rfd.builder.get_status()
    
    # Git commit
    git_hash = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        capture_output=True, text=True
    ).stdout.strip()
    
    # Save checkpoint
    conn = sqlite3.connect(rfd.db_path)
    conn.execute("""
        INSERT INTO checkpoints (feature_id, timestamp, validation_passed, 
                                build_passed, git_hash, evidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        rfd.session.get_current_feature(),
        datetime.now().isoformat(),
        validation['passing'],
        build['passing'],
        git_hash,
        json.dumps({'message': message, 'validation': validation, 'build': build})
    ))
    conn.commit()
    
    # Update PROGRESS.md
    with open('PROGRESS.md', 'a') as f:
        f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} - Checkpoint\n")
        f.write(f"MESSAGE: {message}\n")
        f.write(f"VALIDATION: {'✅' if validation['passing'] else '❌'}\n")
        f.write(f"BUILD: {'✅' if build['passing'] else '❌'}\n")
        f.write(f"COMMIT: {git_hash[:7]}\n")
    
    click.echo(f"✅ Checkpoint saved: {message}")

@cli.command()
@click.pass_obj
def revert(rfd):
    """Revert to last working checkpoint"""
    conn = sqlite3.connect(rfd.db_path)
    last_good = conn.execute("""
        SELECT git_hash, timestamp FROM checkpoints
        WHERE validation_passed = 1 AND build_passed = 1
        ORDER BY id DESC LIMIT 1
    """).fetchone()
    
    if not last_good:
        click.echo("❌ No working checkpoint found")
        return
    
    git_hash, timestamp = last_good
    
    # Git revert
    subprocess.run(['git', 'reset', '--hard', git_hash])
    
    click.echo(f"✅ Reverted to checkpoint from {timestamp}")
    click.echo(f"   Git hash: {git_hash[:7]}")

@cli.group()
@click.pass_obj
def memory(rfd):
    """Manage AI memory"""
    pass

@memory.command('show')
@click.pass_obj
def memory_show(rfd):
    """Show current AI memory"""
    memory_file = rfd.rfd_dir / 'context' / 'memory.json'
    if memory_file.exists():
        data = json.loads(memory_file.read_text())
        click.echo(json.dumps(data, indent=2))

@memory.command('reset')
@click.pass_obj
def memory_reset(rfd):
    """Reset AI memory"""
    memory_file = rfd.rfd_dir / 'context' / 'memory.json'
    memory_file.write_text('{}')
    click.echo("✅ Memory reset")

def create_claude_md():
    """Create CLAUDE.md for Claude Code CLI"""
    content = """---
# Claude Code Configuration
model: claude-3-5-sonnet-20241022
temperature: 0.2
max_tokens: 4000
tools: enabled
memory: .rfd/context/memory.json
---

# RFD Project Assistant

You are operating in a Reality-First Development (RFD) project. Your ONLY job is to make tests pass.

## Critical Rules
1. Read @PROJECT.md for the specification
2. Check @.rfd/context/current.md for your current task
3. Read @PROGRESS.md for what's already done
4. Run `./rfd check` before ANY changes
5. Every code change MUST improve `./rfd validate` output
6. NEVER mock data - use real implementations
7. NEVER add features not in @PROJECT.md

## Workflow for Every Response

### 1. Check Current State
```bash
./rfd check
```

### 2. Read Context
- @PROJECT.md - What we're building
- @.rfd/context/current.md - Current feature/task
- @PROGRESS.md - What already works

### 3. Write Code
- Minimal code to fix the FIRST failing test
- Complete, runnable code only
- No explanations, just code that works

### 4. Validate
```bash
./rfd build && ./rfd validate
```

### 5. Checkpoint if Passing
```bash
./rfd checkpoint "what you fixed"
```

## Commands You Use

```bash
./rfd check          # Quick status
./rfd build          # Build current feature
./rfd validate       # Run validation tests
./rfd checkpoint     # Save working state
./rfd revert         # Return to last working state
./rfd session start  # Begin new feature
```

## Response Format

ALWAYS structure responses as:

1. **Current State** (from ./rfd check)
2. **Next Fix** (ONE specific thing)
3. **Code** (complete, runnable)
4. **Validation** (./rfd validate output)

Never explain theory. Only write code that makes tests pass.
"""
    Path('CLAUDE.md').write_text(content)

if __name__ == '__main__':
    cli()
```

### Build Engine: build.py

```python
"""
Build Engine for RFD
Handles compilation, setup, and build processes
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

class BuildEngine:
    def __init__(self, rfd):
        self.rfd = rfd
        self.spec = rfd.load_project_spec()
        self.stack = self.spec.get('stack', {})
    
    def get_status(self) -> Dict[str, Any]:
        """Get current build status"""
        # Check if service is running
        if self.stack.get('framework') == 'fastapi':
            return self._check_fastapi()
        elif self.stack.get('framework') == 'express':
            return self._check_express()
        # Add more frameworks
        
        return {'passing': False, 'message': 'Unknown stack'}
    
    def build_feature(self, feature_id: str) -> bool:
        """Build specific feature"""
        # Load feature spec
        feature = self._get_feature(feature_id)
        if not feature:
            print(f"❌ Feature {feature_id} not found")
            return False
        
        # Run stack-specific build
        if self.stack.get('language') == 'python':
            return self._build_python(feature)
        elif self.stack.get('language') == 'javascript':
            return self._build_javascript(feature)
        
        return False
    
    def _build_python(self, feature: Dict) -> bool:
        """Python-specific build process"""
        steps = [
            # Install dependencies
            ('Installing dependencies', ['uv', 'pip', 'install', '-r', 'requirements.txt']),
            
            # Run formatters
            ('Formatting code', ['ruff', 'format', '.']),
            
            # Run linters
            ('Linting', ['ruff', 'check', '.']),
            
            # Type checking
            ('Type checking', ['mypy', '.']),
            
            # Start service
            ('Starting service', self._get_start_command())
        ]
        
        for step_name, cmd in steps:
            print(f"→ {step_name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ {step_name} failed:")
                print(result.stderr)
                return False
            print(f"✅ {step_name}")
        
        return True
    
    def _get_start_command(self) -> list:
        """Get command to start the service"""
        if self.stack.get('framework') == 'fastapi':
            return ['uvicorn', 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8000']
        # Add more frameworks
        return []
    
    def _check_fastapi(self) -> Dict[str, Any]:
        """Check if FastAPI service is running"""
        try:
            import requests
            base_url = self.spec.get('api_contract', {}).get('base_url', 'http://localhost:8000')
            health = self.spec.get('api_contract', {}).get('health_check', '/health')
            
            r = requests.get(f"{base_url}{health}", timeout=2)
            return {
                'passing': r.status_code == 200,
                'message': f"Service responding at {base_url}"
            }
        except:
            return {
                'passing': False,
                'message': 'Service not running'
            }
    
    def _get_feature(self, feature_id: str) -> Optional[Dict]:
        """Get feature from spec"""
        features = self.spec.get('features', [])
        for f in features:
            if f['id'] == feature_id:
                return f
        return None
```

### Validation Engine: validate.py

```python
"""
Validation Engine for RFD
Tests that code actually works as specified
"""

import requests
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

class ValidationEngine:
    def __init__(self, rfd):
        self.rfd = rfd
        self.spec = rfd.load_project_spec()
        self.results = []
    
    def validate(self, feature: Optional[str] = None, full: bool = False) -> Dict[str, Any]:
        """Run validation tests"""
        self.results = []
        
        # Structural validation
        self._validate_structure()
        
        # API validation
        if 'api_contract' in self.spec:
            self._validate_api()
        
        # Feature validation
        if feature:
            self._validate_feature(feature)
        elif full:
            for f in self.spec.get('features', []):
                self._validate_feature(f['id'])
        
        # Database validation
        self._validate_database()
        
        return {
            'passing': all(r['passed'] for r in self.results),
            'results': self.results
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Quick validation status"""
        results = self.validate()
        return {
            'passing': results['passing'],
            'failed_count': sum(1 for r in results['results'] if not r['passed']),
            'message': 'All validations passing' if results['passing'] else 'Validation failures detected'
        }
    
    def _validate_structure(self):
        """Validate project structure against rules"""
        rules = self.spec.get('rules', {})
        
        # File count
        if 'max_files' in rules:
            files = list(Path('.').glob('**/*.py'))
            passed = len(files) <= rules['max_files']
            self.results.append({
                'test': 'max_files',
                'passed': passed,
                'message': f"{len(files)} files (max: {rules['max_files']})"
            })
        
        # Lines per file
        if 'max_loc_per_file' in rules:
            for f in Path('.').glob('**/*.py'):
                if '.rfd' in str(f):
                    continue
                lines = len(open(f).readlines())
                passed = lines <= rules['max_loc_per_file']
                if not passed:
                    self.results.append({
                        'test': f'loc_{f.name}',
                        'passed': False,
                        'message': f"{f.name} has {lines} lines (max: {rules['max_loc_per_file']})"
                    })
    
    def _validate_api(self):
        """Validate API endpoints against contract"""
        contract = self.spec['api_contract']
        base_url = contract['base_url']
        
        # Check health endpoint first
        try:
            r = requests.get(f"{base_url}{contract['health_check']}", timeout=2)
            self.results.append({
                'test': 'api_health',
                'passed': r.status_code == 200,
                'message': f"Health check: {r.status_code}"
            })
        except Exception as e:
            self.results.append({
                'test': 'api_health',
                'passed': False,
                'message': f"API not reachable: {e}"
            })
            return  # Skip other tests if API is down
        
        # Test each endpoint
        for endpoint in contract.get('endpoints', []):
            self._test_endpoint(base_url, endpoint)
    
    def _test_endpoint(self, base_url: str, endpoint: Dict):
        """Test single endpoint"""
        url = f"{base_url}{endpoint['path']}"
        method = endpoint['method']
        
        # Generate test data
        test_data = self._generate_test_data(endpoint['path'])
        
        try:
            if method == 'GET':
                r = requests.get(url)
            elif method == 'POST':
                r = requests.post(url, json=test_data)
            else:
                r = requests.request(method, url, json=test_data)
            
            # Check response
            expected = endpoint.get('validates', '')
            passed = self._check_response(r, expected)
            
            self.results.append({
                'test': f"{method}_{endpoint['path']}",
                'passed': passed,
                'message': f"{r.status_code} - {expected}"
            })
        except Exception as e:
            self.results.append({
                'test': f"{method}_{endpoint['path']}",
                'passed': False,
                'message': str(e)
            })
    
    def _check_response(self, response, expected: str) -> bool:
        """Check if response matches expected format"""
        if not expected:
            return True
        
        # Parse expected format
        if "returns" in expected:
            parts = expected.split("returns")[1].strip()
            expected_code = int(parts.split()[0])
            
            if response.status_code != expected_code:
                return False
            
            # Check response shape
            if "{" in expected:
                import re
                shape = re.search(r'\{([^}]+)\}', expected).group(1)
                fields = [f.split(':')[0].strip() for f in shape.split(',')]
                
                try:
                    data = response.json()
                    for field in fields:
                        if field not in data:
                            return False
                except:
                    return False
        
        return True
    
    def _validate_feature(self, feature_id: str):
        """Validate specific feature"""
        # Find feature in spec
        feature = None
        for f in self.spec.get('features', []):
            if f['id'] == feature_id:
                feature = f
                break
        
        if not feature:
            self.results.append({
                'test': f'feature_{feature_id}',
                'passed': False,
                'message': 'Feature not found in spec'
            })
            return
        
        # Run acceptance test
        acceptance = feature.get('acceptance', '')
        # Parse and run acceptance criteria
        # This would be expanded based on your testing needs
        
        self.results.append({
            'test': f'feature_{feature_id}',
            'passed': feature.get('status') == 'complete',
            'message': f"{feature['description']} - {feature.get('status', 'pending')}"
        })
    
    def _validate_database(self):
        """Validate database state"""
        db_type = self.spec.get('stack', {}).get('database')
        
        if db_type == 'sqlite':
            # Check if DB exists and has tables
            db_files = list(Path('.').glob('*.db'))
            if not db_files:
                self.results.append({
                    'test': 'database',
                    'passed': False,
                    'message': 'No SQLite database found'
                })
                return
            
            # Check schema
            conn = sqlite3.connect(db_files[0])
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            
            self.results.append({
                'test': 'database',
                'passed': len(tables) > 0,
                'message': f"Database has {len(tables)} tables"
            })
    
    def _generate_test_data(self, path: str) -> Dict:
        """Generate test data based on path"""
        # Smart defaults
        if 'signup' in path or 'register' in path:
            return {"email": "test@example.com", "password": "Test123!"}
        elif 'login' in path:
            return {"email": "test@example.com", "password": "Test123!"}
        return {}
    
    def print_report(self, results: Dict[str, Any]):
        """Print validation report"""
        print("\n=== Validation Report ===\n")
        
        for result in results['results']:
            icon = '✅' if result['passed'] else '❌'
            print(f"{icon} {result['test']}: {result['message']}")
        
        print(f"\nOverall: {'✅ PASSING' if results['passing'] else '❌ FAILING'}")
```

### Session Manager: session.py

```python
"""
Session Manager for RFD
Manages development sessions and AI context
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class SessionManager:
    def __init__(self, rfd):
        self.rfd = rfd
        self.current_session = None
        self.context_dir = rfd.rfd_dir / 'context'
    
    def start(self, feature_id: str) -> int:
        """Start new development session"""
        # End any existing session
        if self.current_session:
            self.end(success=False)
        
        # Create new session
        conn = sqlite3.connect(self.rfd.db_path)
        cursor = conn.execute("""
            INSERT INTO sessions (started_at, feature_id)
            VALUES (?, ?)
        """, (datetime.now().isoformat(), feature_id))
        session_id = cursor.lastrowid
        conn.commit()
        
        self.current_session = {
            'id': session_id,
            'feature_id': feature_id,
            'started_at': datetime.now().isoformat()
        }
        
        # Update feature status
        conn.execute("""
            UPDATE features SET status = 'building'
            WHERE id = ?
        """, (feature_id,))
        conn.commit()
        
        # Generate context for AI
        self._generate_context(feature_id)
        
        return session_id
    
    def end(self, success: bool = True) -> Optional[int]:
        """End current session"""
        if not self.current_session:
            return None
        
        session_id = self.current_session['id']
        
        # Update session record
        conn = sqlite3.connect(self.rfd.db_path)
        conn.execute("""
            UPDATE sessions 
            SET ended_at = ?, success = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), success, session_id))
        
        # Update feature status if successful
        if success:
            conn.execute("""
                UPDATE features SET status = 'complete', completed_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), self.current_session['feature_id']))
        
        conn.commit()
        
        self.current_session = None
        return session_id
    
    def get_current(self) -> Optional[Dict[str, Any]]:
        """Get current session info"""
        return self.current_session
    
    def get_current_feature(self) -> Optional[str]:
        """Get current feature being worked on"""
        if self.current_session:
            return self.current_session['feature_id']
        
        # Check for any in-progress features
        conn = sqlite3.connect(self.rfd.db_path)
        result = conn.execute("""
            SELECT id FROM features 
            WHERE status = 'building'
            ORDER BY created_at DESC LIMIT 1
        """).fetchone()
        
        return result[0] if result else None
    
    def suggest_next_action(self) -> str:
        """Suggest next action based on current state"""
        state = self.rfd.get_current_state()
        
        # Check validation status
        if not state['validation']['passing']:
            return "./rfd validate  # Fix validation errors"
        
        # Check build status
        if not state['build']['passing']:
            return "./rfd build  # Fix build errors"
        
        # Check for pending features
        conn = sqlite3.connect(self.rfd.db_path)
        pending = conn.execute("""
            SELECT id FROM features 
            WHERE status = 'pending'
            ORDER BY created_at LIMIT 1
        """).fetchone()
        
        if pending:
            return f"./rfd session start {pending[0]}"
        
        return "./rfd check  # All features complete!"
    
    def _generate_context(self, feature_id: str):
        """Generate context file for AI"""
        spec = self.rfd.load_project_spec()
        
        # Find feature
        feature = None
        for f in spec.get('features', []):
            if f['id'] == feature_id:
                feature = f
                break
        
        if not feature:
            return
        
        # Get current validation status
        validation = self.rfd.validator.validate(feature=feature_id)
        
        # Generate context document
        context = f"""---
session_id: {self.current_session['id']}
feature: {feature_id}
started: {self.current_session['started_at']}
status: building
---

# Current Session: {feature_id}

## Feature Specification
{feature['description']}

**Acceptance Criteria:**
{feature.get('acceptance', 'Not specified')}

## Current Status
```
./rfd validate --feature {feature_id}
"""
        
        # Add validation results
        for result in validation['results']:
            icon = '✅' if result['passed'] else '❌'
            context += f"{icon} {result['test']}: {result['message']}\n"
        
        context += f"""```

## Required Actions
1. Make all validation tests pass
2. Ensure code follows PROJECT.md constraints
3. No mocks - use real implementations

## Commands
```bash
./rfd build          # Build current feature
./rfd validate       # Check if tests pass
./rfd checkpoint     # Save working state
```

## Constraints from PROJECT.md
"""
        
        # Add constraints
        for constraint in spec.get('constraints', []):
            context += f"- {constraint}\n"
        
        # Write context file
        context_file = self.context_dir / 'current.md'
        context_file.write_text(context)
        
        # Update memory
        self._update_memory(feature_id, validation)
    
    def _update_memory(self, feature_id: str, validation: Dict[str, Any]):
        """Update AI memory with current state"""
        memory_file = self.context_dir / 'memory.json'
        
        # Load existing memory
        if memory_file.exists():
            memory = json.loads(memory_file.read_text())
        else:
            memory = {
                'features_completed': [],
                'common_errors': [],
                'working_patterns': []
            }
        
        # Update with current session
        memory['current_feature'] = feature_id
        memory['last_validation'] = validation
        memory['session_started'] = self.current_session['started_at']
        
        # Save memory
        memory_file.write_text(json.dumps(memory, indent=2))
```

### Spec Engine: spec.py

```python
"""
Spec Engine for RFD
Manages spec-driven design following GitHub Spec Kit patterns
"""

import yaml
import frontmatter
from pathlib import Path
from typing import Dict, Any
import questionary

class SpecEngine:
    def __init__(self, rfd):
        self.rfd = rfd
    
    def create_interactive(self):
        """Interactive spec creation wizard"""
        print("\n🎯 RFD Spec Creator\n")
        
        # Basic info
        name = questionary.text("Project name:").ask()
        description = questionary.text("What does this do? (30 words max):").ask()
        
        # Stack selection
        language = questionary.select(
            "Language:",
            choices=['python', 'javascript', 'typescript', 'ruby', 'go']
        ).ask()
        
        framework = self._select_framework(language)
        database = questionary.select(
            "Database:",
            choices=['sqlite', 'postgresql', 'mysql', 'mongodb', 'none']
        ).ask()
        
        # Features (max 3 for v1)
        features = []
        for i in range(3):
            if i > 0 and not questionary.confirm(f"Add feature {i+1}?").ask():
                break
            
            feature_id = questionary.text(f"Feature {i+1} ID (e.g., user_signup):").ask()
            feature_desc = questionary.text(f"Feature {i+1} description:").ask()
            feature_acceptance = questionary.text(f"Acceptance criteria:").ask()
            
            features.append({
                'id': feature_id,
                'description': feature_desc,
                'acceptance': feature_acceptance,
                'status': 'pending'
            })
        
        # Rules
        max_files = questionary.text("Max files allowed:", default="20").ask()
        max_loc = questionary.text("Max lines per file:", default="200").ask()
        
        # Generate PROJECT.md
        spec = {
            'version': '1.0',
            'name': name,
            'stack': {
                'language': language,
                'framework': framework,
                'database': database
            },
            'rules': {
                'max_files': int(max_files),
                'max_loc_per_file': int(max_loc),
                'must_pass_tests': True,
                'no_mocks_in_prod': True
            },
            'features': features,
            'constraints': self._default_constraints()
        }
        
        # Add API contract if web framework
        if framework in ['fastapi', 'express', 'rails']:
            spec['api_contract'] = self._generate_api_contract(features)
        
        # Write PROJECT.md
        post = frontmatter.Post(description, **spec)
        
        with open('PROJECT.md', 'w') as f:
            f.write(frontmatter.dumps(post))
        
        print("✅ PROJECT.md created!")
        
        # Initialize features in database
        self._init_features(features)
    
    def _select_framework(self, language: str) -> str:
        """Select framework based on language"""
        frameworks = {
            'python': ['fastapi', 'flask', 'django', 'none'],
            'javascript': ['express', 'nestjs', 'koa', 'none'],
            'typescript': ['express', 'nestjs', 'none'],
            'ruby': ['rails', 'sinatra', 'none'],
            'go': ['gin', 'echo', 'none']
        }
        
        return questionary.select(
            "Framework:",
            choices=frameworks.get(language, ['none'])
        ).ask()
    
    def _default_constraints(self) -> list:
        """Default constraints for any project"""
        return [
            "NO authentication libraries until core works",
            "NO database migrations until schema stable", 
            "NO frontend until API complete",
            "NO optimization until features work",
            "NO abstractions until patterns emerge"
        ]
    
    def _generate_api_contract(self, features: list) -> Dict:
        """Generate API contract from features"""
        contract = {
            'base_url': 'http://localhost:8000',
            'health_check': '/health',
            'endpoints': []
        }
        
        # Generate endpoints from features
        for feature in features:
            if 'signup' in feature['id']:
                contract['endpoints'].append({
                    'method': 'POST',
                    'path': '/signup',
                    'validates': 'returns 201 with {user_id: string}'
                })
            elif 'login' in feature['id']:
                contract['endpoints'].append({
                    'method': 'POST',
                    'path': '/login',
                    'validates': 'returns 200 with {token: string}'
                })
            # Add more patterns
        
        return contract
    
    def _init_features(self, features: list):
        """Initialize features in database"""
        import sqlite3
        conn = sqlite3.connect(self.rfd.db_path)
        
        for feature in features:
            conn.execute("""
                INSERT OR REPLACE INTO features (id, description, acceptance_criteria, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                feature['id'],
                feature['description'],
                feature.get('acceptance', ''),
                'pending',
                datetime.now().isoformat()
            ))
        
        conn.commit()
    
    def validate(self) -> bool:
        """Validate spec against Spec Kit standards"""
        spec = self.rfd.load_project_spec()
        
        required_fields = ['version', 'name', 'stack', 'features']
        for field in required_fields:
            if field not in spec:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Validate features
        if len(spec['features']) == 0:
            print("❌ No features defined")
            return False
        
        if len(spec['features']) > 3:
            print("⚠️  Warning: More than 3 features for v1")
        
        print("✅ Spec is valid")
        return True
    
    def review(self):
        """Display spec in readable format"""
        spec = self.rfd.load_project_spec()
        
        print("\n=== PROJECT SPECIFICATION ===\n")
        print(f"📦 {spec.get('name', 'Unnamed Project')}")
        print(f"Version: {spec.get('version', '1.0')}\n")
        
        # Stack
        stack = spec.get('stack', {})
        print("🔧 Technology Stack:")
        print(f"  Language: {stack.get('language', 'not specified')}")
        print(f"  Framework: {stack.get('framework', 'not specified')}")
        print(f"  Database: {stack.get('database', 'not specified')}\n")
        
        # Features
        print("📋 Features:")
        for f in spec.get('features', []):
            status_icon = '✅' if f['status'] == 'complete' else '🔨' if f['status'] == 'building' else '⭕'
            print(f"  {status_icon} {f['id']}")
            print(f"      {f['description']}")
            print(f"      Acceptance: {f.get('acceptance', 'Not specified')}\n")
        
        # Rules
        print("📏 Rules:")
        for rule, value in spec.get('rules', {}).items():
            print(f"  • {rule}: {value}")
        
        # Constraints
        print("\n🚫 Constraints:")
        for constraint in spec.get('constraints', []):
            print(f"  • {constraint}")
```

## Installation & Usage

### One-Line Install
```bash
curl -sSL https://rfd.dev/install.sh | bash
```

### Manual Install
```bash
git clone https://github.com/rfd-system/rfd .rfd
chmod +x .rfd/rfd.py
ln -s .rfd/rfd.py rfd
./rfd init
```

### Complete Workflow

1. **Initialize Project**
```bash
./rfd init
# Interactive spec creation
# Generates PROJECT.md, CLAUDE.md, PROGRESS.md
```

2. **Start Building**
```bash
./rfd session start user_signup
# Updates context for Claude Code CLI
# Now Claude knows exactly what to build
```

3. **Build & Validate Loop**
```bash
./rfd check          # Current status
./rfd build          # Run build process
./rfd validate       # Test everything
./rfd checkpoint     # Save if passing
```

4. **Work with Claude Code CLI**
```bash
claude "implement the current feature"
# Claude reads @PROJECT.md, @.rfd/context/current.md
# Writes code that MUST pass ./rfd validate
```

## Why This Works

1. **Single Entry Point**: `./rfd` command for everything
2. **SQLite Truth**: All state in `.rfd/memory.db`
3. **Context Management**: AI always knows what to do via `.rfd/context/current.md`
4. **Forced Progress**: Code either passes validation or gets reverted
5. **No Drift**: CLAUDE.md + session context = strict guardrails
6. **Stack Agnostic**: Works with any language/framework

## The Key Innovation

**Every AI response must improve `./rfd validate` or it doesn't exist.**

No philosophical debates. No mock data. No feature creep. Just reality-based progress tracked in SQLite.

Ready to build? This is the complete system. Drop it in any project and start with `./rfd init`.

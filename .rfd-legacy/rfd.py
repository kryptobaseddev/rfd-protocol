#!/usr/bin/env python3
"""
RFD: Reality-First Development System (Bulletproof Edition)
Robust, production-ready implementation with comprehensive error handling
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

# Check for required modules and provide helpful errors
try:
    import click
except ImportError:
    print("❌ Click not installed. Run: pip install click")
    sys.exit(1)

try:
    import frontmatter
except ImportError:
    print("❌ Frontmatter not installed. Run: pip install python-frontmatter")
    sys.exit(1)


class BulletproofRFD:
    """Production-ready RFD with comprehensive error handling"""
    
    def __init__(self, auto_setup=True):
        self.root = Path.cwd()
        self.rfd_dir = self.root / ".rfd"
        self.db_path = self.rfd_dir / "memory.db"
        self.modules_loaded = False
        
        if auto_setup:
            self._ensure_environment()
    
    def _ensure_environment(self):
        """Ensure environment is properly set up"""
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            sys.exit(1)
        
        # Create structure if needed
        if not self.rfd_dir.exists():
            print("📁 Creating RFD structure...")
            self._init_structure()
        
        # Initialize database
        self._init_database()
        
        # Load modules with error handling
        self._load_modules()
    
    def _init_structure(self):
        """Create RFD directory structure"""
        dirs = [
            self.rfd_dir,
            self.rfd_dir / "context",
            self.rfd_dir / "context" / "checkpoints",
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        # Create default files
        memory_file = self.rfd_dir / "context" / "memory.json"
        if not memory_file.exists():
            memory_file.write_text("{}")
    
    def _init_database(self):
        """Initialize SQLite database with all tables"""
        conn = sqlite3.connect(self.db_path)
        
        # Features table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS features (
                id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
        """)
        
        # Checkpoints table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY,
                feature_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validation_passed BOOLEAN,
                build_passed BOOLEAN,
                git_hash TEXT,
                evidence JSON
            )
        """)
        
        # Sessions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                feature_id TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TEXT,
                success BOOLEAN,
                errors JSON
            )
        """)
        
        # Memory table for key-value storage
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_modules(self):
        """Load RFD modules with fallback to stubs"""
        try:
            # Add .rfd to path
            if str(self.rfd_dir) not in sys.path:
                sys.path.insert(0, str(self.rfd_dir))
            
            # Try to import modules
            try:
                from build import BuildEngine
                from session import SessionManager
                from spec import SpecEngine
                from validation import ValidationEngine
                
                self.builder = BuildEngine(self)
                self.validator = ValidationEngine(self)
                self.spec = SpecEngine(self)
                self.session = SessionManager(self)
                self.modules_loaded = True
                
            except ImportError as e:
                print(f"⚠️  Using stub modules: {e}")
                # Create stub implementations
                self.builder = StubModule("BuildEngine")
                self.validator = StubModule("ValidationEngine")
                self.spec = StubModule("SpecEngine") 
                self.session = StubModule("SessionManager")
                
        except Exception as e:
            print(f"⚠️  Module loading error: {e}")
            self.modules_loaded = False
    
    def load_project_spec(self) -> Dict:
        """Load PROJECT.md with comprehensive fallbacks"""
        # Try PROJECT.md first
        project_file = self.root / "PROJECT.md"
        if project_file.exists():
            try:
                with open(project_file) as f:
                    post = frontmatter.load(f)
                    if post.metadata:
                        return post.metadata
            except Exception as e:
                print(f"⚠️  Error reading PROJECT.md: {e}")
        
        # Try .rfd/spec.json
        spec_file = self.rfd_dir / "spec.json"
        if spec_file.exists():
            try:
                return json.loads(spec_file.read_text())
            except Exception as e:
                print(f"⚠️  Error reading spec.json: {e}")
        
        # Return minimal default
        return {
            "name": "unnamed-project",
            "version": "0.0.1",
            "stack": {"language": "python"},
            "features": []
        }
    
    def get_status(self) -> Dict:
        """Get comprehensive project status"""
        status = {
            "environment": self._check_environment(),
            "modules": self.modules_loaded,
            "features": [],
            "validation": None,
            "build": None
        }
        
        # Get features from spec
        spec = self.load_project_spec()
        for feature in spec.get("features", []):
            status["features"].append({
                "id": feature.get("id"),
                "status": feature.get("status", "pending"),
                "description": feature.get("description", "")
            })
        
        # Check validation status
        if self.modules_loaded and hasattr(self.validator, 'get_status'):
            status["validation"] = self.validator.get_status()
        
        # Check build status
        if self.modules_loaded and hasattr(self.builder, 'get_status'):
            status["build"] = self.builder.get_status()
        
        return status
    
    def _check_environment(self) -> Dict:
        """Check environment health"""
        checks = {
            "python": sys.version,
            "venv": bool(os.environ.get("VIRTUAL_ENV")),
            "rfd_dir": self.rfd_dir.exists(),
            "database": self.db_path.exists(),
            "modules": self.modules_loaded
        }
        return checks
    
    def checkpoint(self, message: str) -> bool:
        """Save a checkpoint with current state"""
        try:
            # Get git hash
            git_hash = "no-git"
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    git_hash = result.stdout.strip()
            except:
                pass
            
            # Get current validation status
            validation_passed = False
            if self.modules_loaded:
                try:
                    results = self.validator.validate()
                    validation_passed = all(r.get("passed") for r in results)
                except:
                    pass
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO checkpoints (
                    timestamp, validation_passed, git_hash, evidence
                ) VALUES (?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                validation_passed,
                git_hash,
                json.dumps({"message": message})
            ))
            conn.commit()
            conn.close()
            
            # Update PROGRESS.md
            progress_file = self.root / "PROGRESS.md"
            with open(progress_file, "a") as f:
                f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} - Checkpoint\n")
                f.write(f"MESSAGE: {message}\n")
                f.write(f"VALIDATION: {'✅' if validation_passed else '❌'}\n")
                f.write(f"COMMIT: {git_hash[:7]}\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Checkpoint failed: {e}")
            return False


class StubModule:
    """Stub module for when real modules can't load"""
    
    def __init__(self, name):
        self.name = name
    
    def __getattr__(self, item):
        """Return a callable that warns about missing module"""
        def stub_method(*args, **kwargs):
            print(f"⚠️  {self.name}.{item} not available - module not loaded")
            return None
        return stub_method


# CLI Commands
@click.group()
@click.pass_context
def cli(ctx):
    """RFD: Reality-First Development Protocol"""
    ctx.obj = BulletproofRFD()


@cli.command()
@click.pass_obj
def check(rfd):
    """Check project status"""
    status = rfd.get_status()
    
    print("=== RFD Status Check ===\n")
    
    # Environment
    env = status["environment"]
    print("🔧 Environment:")
    print(f"  Python: {env['python']}")
    print(f"  Virtual Env: {'✅' if env['venv'] else '❌'}")
    print(f"  RFD Dir: {'✅' if env['rfd_dir'] else '❌'}")
    print(f"  Database: {'✅' if env['database'] else '❌'}")
    print(f"  Modules: {'✅' if env['modules'] else '❌'}")
    
    # Features
    if status["features"]:
        print("\n📦 Features:")
        for feature in status["features"]:
            icon = "✅" if feature["status"] == "complete" else "🔨"
            print(f"  {icon} {feature['id']}: {feature['description'][:50]}")
    
    # Validation
    if status["validation"]:
        print(f"\n📋 Validation: {'✅' if status['validation'] else '❌'}")
    
    # Build
    if status["build"]:
        print(f"🔨 Build: {'✅' if status['build'] else '❌'}")
    
    # Suggest next action
    print("\n→ Next: ", end="")
    if not env["venv"]:
        print("python3 setup.py  # Setup environment")
    elif not env["modules"]:
        print("./rfd init  # Initialize project")
    elif status["features"]:
        pending = [f for f in status["features"] if f["status"] != "complete"]
        if pending:
            print(f"./rfd build {pending[0]['id']}  # Build next feature")
        else:
            print("All features complete! 🎉")
    else:
        print("./rfd init  # Create project spec")


@cli.command()
@click.pass_obj
def init(rfd):
    """Initialize RFD project"""
    print("🚀 Initializing RFD project...")
    
    # Ensure structure exists
    rfd._init_structure()
    rfd._init_database()
    
    print("✅ RFD initialized!")
    print("\nNext steps:")
    print("  1. Create PROJECT.md with your specifications")
    print("  2. Run: ./rfd check")
    print("  3. Start building features!")


@cli.command()
@click.argument('feature_id', required=False)
@click.pass_obj
def build(rfd, feature_id):
    """Build a feature"""
    if not feature_id:
        # Get current feature from context
        context_file = rfd.rfd_dir / "context" / "current.md"
        if context_file.exists():
            try:
                with open(context_file) as f:
                    content = frontmatter.load(f)
                    feature_id = content.metadata.get("feature")
            except:
                pass
        
        if not feature_id:
            print("❌ No feature specified. Use: ./rfd build <feature>")
            return
    
    print(f"🔨 Building feature: {feature_id}")
    
    if rfd.modules_loaded:
        success = rfd.builder.build_feature(feature_id)
        if success:
            print("✅ Build successful!")
        else:
            print("❌ Build failed - check errors above")
    else:
        print("❌ Build modules not loaded. Run: python3 setup.py")


@cli.command()
@click.option('--feature', help='Validate specific feature')
@click.pass_obj
def validate(rfd, feature):
    """Validate project or feature"""
    print("=== Validation Report ===\n")
    
    if not rfd.modules_loaded:
        print("❌ Validation modules not loaded")
        return
    
    if feature:
        validation_output = rfd.validator.validate_feature(feature)
    else:
        validation_output = rfd.validator.validate()
    
    # Extract results list from validation output
    if isinstance(validation_output, dict) and "results" in validation_output:
        results = validation_output["results"]
    else:
        results = validation_output if isinstance(validation_output, list) else []
    
    # Display results
    passed = 0
    failed = 0
    
    for result in results:
        if result.get("passed"):
            print(f"✅ {result['test']}: {result['message']}")
            passed += 1
        else:
            print(f"❌ {result['test']}: {result['message']}")
            failed += 1
    
    print(f"\nOverall: {'✅ PASSING' if failed == 0 else '❌ FAILING'}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")


@cli.command()
@click.argument('message')
@click.pass_obj
def checkpoint(rfd, message):
    """Save a checkpoint"""
    if rfd.checkpoint(message):
        print(f"✅ Checkpoint saved: {message}")
    else:
        print("❌ Checkpoint failed")


@cli.group()
@click.pass_obj
def session(rfd):
    """Session management commands"""
    pass


@session.command('start')
@click.argument('feature_id')
@click.pass_obj
def session_start(rfd, feature_id):
    """Start a new session"""
    if rfd.modules_loaded:
        session_id = rfd.session.create_session(feature_id)
        print(f"✅ Session {session_id} started for {feature_id}")
    else:
        # Fallback: write to context file
        context_file = rfd.rfd_dir / "context" / "current.md"
        content = f"""---
session_id: 1
feature: {feature_id}
started: {datetime.now().isoformat()}
status: building
---

# Current Session: {feature_id}
"""
        context_file.write_text(content)
        print(f"✅ Session started for {feature_id}")


@session.command('status')
@click.pass_obj
def session_status(rfd):
    """Check session status"""
    context_file = rfd.rfd_dir / "context" / "current.md"
    if context_file.exists():
        with open(context_file) as f:
            content = frontmatter.load(f)
            meta = content.metadata
            print(f"📊 Current Session:")
            print(f"  Feature: {meta.get('feature', 'unknown')}")
            print(f"  Status: {meta.get('status', 'unknown')}")
            print(f"  Started: {meta.get('started', 'unknown')}")
    else:
        print("❌ No active session")


if __name__ == "__main__":
    cli()
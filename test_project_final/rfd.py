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

from build import BuildEngine
from validation import ValidationEngine
from spec import SpecEngine
from session import SessionManager

class RFD:
    """Main RFD orchestrator - coordinates all subsystems"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.rfd_dir = self.root / '.rfd'
        self.db_path = self.rfd_dir / 'memory.db'
        
        # Initialize subsystems
        self._init_structure()
        self._init_database()
        
        # Load modules with proper imports
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
        """Load and parse PROJECT.md - supports both frontmatter and standard markdown"""
        project_file = self.root / 'PROJECT.md'
        if not project_file.exists():
            return {}
        
        with open(project_file, 'r') as f:
            content = f.read()
        
        # Try frontmatter format first
        try:
            post = frontmatter.loads(content)
            if post.metadata:  # Has frontmatter
                return post.metadata
        except:
            pass
        
        # Parse as standard markdown
        return self._parse_markdown_spec(content)
    
    def _parse_markdown_spec(self, content: str) -> Dict[str, Any]:
        """Parse standard markdown PROJECT.md into spec format"""
        lines = content.split('\n')
        spec = {
            'version': '1.0',
            'name': '',
            'description': '',
            'features': [],
            'stack': {},
            'rules': {}
        }
        
        current_section = None
        current_feature = None
        current_feature_content = []
        
        for line in lines:
            line = line.strip()
            
            # Main title (h1)
            if line.startswith('# ') and not spec['name']:
                spec['name'] = line[2:].strip()
            
            # Section headers (h2)
            elif line.startswith('## '):
                section_title = line[3:].strip().lower()
                if 'overview' in section_title:
                    current_section = 'overview'
                elif 'feature' in section_title:
                    current_section = 'features'
                elif 'technology' in section_title or 'stack' in section_title:
                    current_section = 'stack'
                else:
                    current_section = section_title
                continue
            
            # Feature headers (h3)
            elif line.startswith('### '):
                if current_section == 'features':
                    # Save previous feature
                    if current_feature:
                        spec['features'].append(current_feature)
                    
                    # Start new feature
                    feature_title = line[4:].strip()
                    feature_id = self._generate_feature_id(feature_title)
                    current_feature = {
                        'id': feature_id,
                        'title': feature_title,
                        'description': '',
                        'acceptance': [],
                        'status': 'pending'
                    }
                    current_feature_content = []
                continue
            
            # Content processing
            if current_section == 'overview' and line and not line.startswith('#'):
                if spec['description']:
                    spec['description'] += ' ' + line
                else:
                    spec['description'] = line
            
            elif current_section == 'features' and current_feature:
                if line.startswith('**Description**:'):
                    current_feature['description'] = line.replace('**Description**:', '').strip()
                elif line.startswith('**Acceptance Criteria**:'):
                    current_feature_content.append('CRITERIA_START')
                elif line.startswith('- ') and 'CRITERIA_START' in current_feature_content:
                    current_feature['acceptance'].append(line[2:].strip())
                elif line and not line.startswith('**') and not line.startswith('###'):
                    current_feature_content.append(line)
            
            elif current_section == 'stack' and line and not line.startswith('#'):
                # Parse technology stack info
                if 'python' in line.lower():
                    spec['stack']['language'] = 'python'
                if 'flask' in line.lower():
                    spec['stack']['framework'] = 'flask'
                if 'json' in line.lower() and 'file' in line.lower():
                    spec['stack']['database'] = 'json'
        
        # Save last feature
        if current_feature:
            spec['features'].append(current_feature)
        
        return spec
    
    def _generate_feature_id(self, title: str) -> str:
        """Generate feature ID from title"""
        title = title.lower().strip()
        
        # If title already looks like an ID (no spaces, underscores ok), use as-is
        if ' ' not in title and not title.startswith('feature'):
            return title
        
        # Extract feature name after "feature N:"
        if ':' in title:
            title = title.split(':', 1)[1].strip()
        
        # Remove "feature N" prefix if present
        import re
        title = re.sub(r'^feature\s+\d+\s*:?\s*', '', title)
        
        # Convert to snake_case
        feature_id = re.sub(r'[^a-z0-9\s]', '', title)
        feature_id = re.sub(r'\s+', '_', feature_id.strip())
        return feature_id
    
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

    def checkpoint(self, message: str):
        """Save checkpoint with current state"""
        # Get current state
        validation = self.validator.validate()
        build = self.builder.get_status()
        
        # Git commit
        try:
            git_hash = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True
            ).stdout.strip()
        except:
            git_hash = "no-git"
        
        # Save checkpoint
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO checkpoints (feature_id, timestamp, validation_passed, 
                                    build_passed, git_hash, evidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.session.get_current_feature(),
            datetime.now().isoformat(),
            validation['passing'],
            build['passing'],
            git_hash,
            json.dumps({'message': message, 'validation': validation, 'build': build})
        ))
        conn.commit()
        
        # Update PROGRESS.md
        progress_file = self.root / 'PROGRESS.md'
        with open(progress_file, 'a') as f:
            f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} - Checkpoint\n")
            f.write(f"MESSAGE: {message}\n")
            f.write(f"VALIDATION: {'✅' if validation['passing'] else '❌'}\n")
            f.write(f"BUILD: {'✅' if build['passing'] else '❌'}\n")
            f.write(f"COMMIT: {git_hash[:7]}\n")

    def revert_to_last_checkpoint(self):
        """Revert to last working checkpoint"""
        conn = sqlite3.connect(self.db_path)
        # CRITICAL FIX: Allow revert with validation-only checkpoints
        # Try to find a checkpoint with both validation AND build passing
        last_good = conn.execute("""
            SELECT git_hash, timestamp, validation_passed, build_passed FROM checkpoints
            WHERE validation_passed = 1 AND build_passed = 1
            ORDER BY id DESC LIMIT 1
        """).fetchone()
        
        # If no perfect checkpoint, try validation-only
        if not last_good:
            last_good = conn.execute("""
                SELECT git_hash, timestamp, validation_passed, build_passed FROM checkpoints
                WHERE validation_passed = 1
                ORDER BY id DESC LIMIT 1
            """).fetchone()
        
        if not last_good:
            return False, "No checkpoint with passing validation found"
        
        git_hash, timestamp, val_passed, build_passed = last_good
        
        # Git revert
        try:
            subprocess.run(['git', 'reset', '--hard', git_hash], check=True)
            status = "validation+build" if build_passed else "validation-only"
            return True, f"Reverted to {status} checkpoint from {timestamp} (Git hash: {git_hash[:7]})"
        except subprocess.CalledProcessError:
            return False, "Git revert failed"
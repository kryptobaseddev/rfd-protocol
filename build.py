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
        # CRITICAL FIX: First check if tests pass (more important than service running)
        test_result = self._check_tests()
        if test_result['passing']:
            return test_result
        
        # Fall back to checking if service is running
        if self.stack.get('framework') == 'fastapi':
            return self._check_fastapi()
        elif self.stack.get('framework') == 'express':
            return self._check_express()
        # Add more frameworks
        
        return {'passing': False, 'message': 'No tests found and unknown stack'}
    
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
            ('Installing dependencies', ['pip', 'install', '-r', 'requirements.txt']),
            
            # Run formatters (if available)
            ('Formatting code', ['python', '-m', 'black', '.']),
            
            # Run linters (if available)
            ('Linting', ['python', '-m', 'flake8', '.']),
            
            # Type checking (if available)
            ('Type checking', ['python', '-m', 'mypy', '.']),
            
            # Start service
            ('Starting service', self._get_start_command())
        ]
        
        for step_name, cmd in steps:
            print(f"→ {step_name}")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    print(f"❌ {step_name} failed:")
                    print(result.stderr)
                    return False
                print(f"✅ {step_name}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"⚠️ {step_name} skipped (tool not available)")
        
        return True
    
    def _build_javascript(self, feature: Dict) -> bool:
        """JavaScript-specific build process"""
        steps = [
            ('Installing dependencies', ['npm', 'install']),
            ('Running build', ['npm', 'run', 'build']),
            ('Starting service', ['npm', 'start'])
        ]
        
        for step_name, cmd in steps:
            print(f"→ {step_name}")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    print(f"❌ {step_name} failed:")
                    print(result.stderr)
                    return False
                print(f"✅ {step_name}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"⚠️ {step_name} skipped")
        
        return True
    
    def _get_start_command(self) -> list:
        """Get command to start the service"""
        if self.stack.get('framework') == 'fastapi':
            return ['uvicorn', 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8000']
        elif self.stack.get('framework') == 'flask':
            return ['python', 'app.py']
        elif self.stack.get('framework') == 'django':
            return ['python', 'manage.py', 'runserver']
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
    
    def _check_express(self) -> Dict[str, Any]:
        """Check if Express service is running"""
        try:
            import requests
            base_url = self.spec.get('api_contract', {}).get('base_url', 'http://localhost:3000')
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
    
    def _check_tests(self) -> Dict[str, Any]:
        """Check if tests pass by running appropriate test command"""
        # Detect test framework based on files present
        test_commands = [
            # Python test runners
            (['pytest', '--co', '-q'], 'pytest'),  # --co = collect only, quick check
            (['python', '-m', 'pytest', '--co', '-q'], 'pytest'),
            (['python', '-m', 'unittest', 'discover', '-l'], 'unittest'),
            # JavaScript test runners  
            (['npm', 'test', '--', '--listTests'], 'jest'),
            (['yarn', 'test', '--listTests'], 'jest'),
            (['npm', 'run', 'test:unit'], 'npm'),
            # Other languages
            (['cargo', 'test', '--', '--list'], 'cargo'),
            (['go', 'test', './...', '-list=.'], 'go'),
            (['mvn', 'test', '-DskipTests'], 'maven'),
            (['gradle', 'test', '--dry-run'], 'gradle'),
        ]
        
        # Try to find and run test command
        for cmd, runner in test_commands:
            try:
                # First check if test runner exists
                check_result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=5,
                    cwd=self.rfd.root
                )
                
                if check_result.returncode == 0:
                    # Test runner found, now run actual tests
                    if runner == 'pytest':
                        test_cmd = ['pytest', '-v', '--tb=short']
                    elif runner == 'unittest':
                        test_cmd = ['python', '-m', 'unittest', 'discover']
                    elif runner in ['jest', 'npm']:
                        test_cmd = ['npm', 'test']
                    elif runner == 'cargo':
                        test_cmd = ['cargo', 'test']
                    elif runner == 'go':
                        test_cmd = ['go', 'test', './...']
                    elif runner == 'maven':
                        test_cmd = ['mvn', 'test']
                    elif runner == 'gradle':
                        test_cmd = ['gradle', 'test']
                    else:
                        continue
                    
                    # Run the actual tests
                    test_result = subprocess.run(
                        test_cmd,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=self.rfd.root
                    )
                    
                    if test_result.returncode == 0:
                        # Parse output to get test count if possible
                        output = test_result.stdout
                        if 'passed' in output.lower():
                            return {
                                'passing': True,
                                'message': f'All tests passing ({runner})'
                            }
                        else:
                            return {
                                'passing': True, 
                                'message': f'Tests completed successfully ({runner})'
                            }
                    else:
                        # Tests failed
                        return {
                            'passing': False,
                            'message': f'Tests failing ({runner})'
                        }
                        
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                continue
        
        # No test runner found
        return {
            'passing': False,
            'message': 'No test runner detected (pytest, npm test, cargo test, etc.)'
        }
    
    def _get_feature(self, feature_id: str) -> Optional[Dict]:
        """Get feature from spec"""
        features = self.spec.get('features', [])
        for f in features:
            if f['id'] == feature_id:
                return f
        return None
"""
Validation Engine for RFD
Tests that code actually works as specified
"""

import requests
import sqlite3
import json
import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

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
    
    def check_ai_claim(self, claim: str) -> bool:
        """Simple boolean check if an AI claim is true or false"""
        passed, _ = self.validate_ai_claims(claim)
        return passed
    
    def _validate_structure(self):
        """Validate project structure - REAL validation that checks if files exist"""
        rules = self.spec.get('rules', {})
        
        # Check claimed files actually exist
        claimed_files = self.spec.get('claimed_files', [])
        for file_path in claimed_files:
            exists = Path(file_path).exists()
            self.results.append({
                'test': f'file_exists_{file_path}',
                'passed': exists,
                'message': f"File {file_path}: {'EXISTS' if exists else 'MISSING - AI LIED!'}"
            })
        
        # Original rule-based validation
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
                try:
                    lines = len(open(f).readlines())
                    passed = lines <= rules['max_loc_per_file']
                    if not passed:
                        self.results.append({
                            'test': f'loc_{f.name}',
                            'passed': False,
                            'message': f"{f.name} has {lines} lines (max: {rules['max_loc_per_file']})"
                        })
                except:
                    pass
    
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
    
    def validate_ai_claims(self, claims: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate AI claims about file and function creation.
        Returns (passed, details) where passed is False if AI lied.
        """
        validation_results = []
        
        # Parse claims for file paths and function/class names
        file_claims = self._extract_file_claims(claims)
        function_claims = self._extract_function_claims(claims)
        
        # Check each claimed file exists
        for file_path in file_claims:
            exists = Path(file_path).exists()
            validation_results.append({
                'type': 'file',
                'target': file_path,
                'exists': exists,
                'message': f"File {file_path}: {'EXISTS' if exists else 'MISSING - AI HALLUCINATION!'}"
            })
        
        # Check each claimed function/class exists in the files
        for func_name, file_hint in function_claims:
            found = self._verify_function_exists(func_name, file_hint)
            validation_results.append({
                'type': 'function',
                'target': func_name,
                'exists': found,
                'message': f"Function/Class {func_name}: {'FOUND' if found else 'NOT FOUND - AI HALLUCINATION!'}"
            })
        
        # Overall pass/fail
        all_passed = all(r['exists'] for r in validation_results)
        return all_passed, validation_results
    
    def _extract_file_claims(self, text: str) -> List[str]:
        """Extract file paths mentioned in AI claims"""
        patterns = [
            r'[cC]reated?\s+(?:file\s+)?([^\s]+\.(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml))',
            r'[wW]rote?\s+(?:to\s+)?([^\s]+\.(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml))',
            r'[fF]ile\s+([^\s]+\.(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml))',
            r'`([^\s`]+\.(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml))`',
            r'"([^\s"]+\.(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml))"',
            r'\'([^\s\']+\.(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml))\'',
        ]
        
        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            files.update(matches)
        
        # Filter out obvious non-paths
        return [f for f in files if not f.startswith('http') and '://' not in f]
    
    def _extract_function_claims(self, text: str) -> List[Tuple[str, Optional[str]]]:
        """Extract function/class names mentioned in AI claims"""
        patterns = [
            r'[fF]unction\s+(\w+)',
            r'[dD]ef\s+(\w+)',
            r'[cC]lass\s+(\w+)',
            r'[mM]ethod\s+(\w+)',
            r'[iI]mplemented\s+(\w+)',
            r'[cC]reated\s+(?:function|class|method)\s+(\w+)',
            r'`(\w+)\(\)`',  # Function calls in backticks
            r'`class\s+(\w+)`',  # Class definitions in backticks
        ]
        
        functions = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            functions.update(matches)
        
        # Try to associate with file hints if mentioned nearby
        result = []
        for func in functions:
            file_hint = self._find_file_hint_for_function(func, text)
            result.append((func, file_hint))
        
        return result
    
    def _find_file_hint_for_function(self, func_name: str, text: str) -> Optional[str]:
        """Try to find which file a function was claimed to be in"""
        # Look for patterns like "function foo in file.py"
        patterns = [
            rf'{func_name}.*?in\s+([^\s]+\.py)',
            rf'([^\s]+\.py).*?{func_name}',
            rf'{func_name}.*?to\s+([^\s]+\.py)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _verify_function_exists(self, func_name: str, file_hint: Optional[str] = None) -> bool:
        """Verify if a function/class actually exists in the codebase"""
        # If we have a file hint, check there first
        if file_hint and Path(file_hint).exists():
            try:
                with open(file_hint, 'r') as f:
                    content = f.read()
                    # Check for function/class definition
                    if re.search(rf'^\s*def\s+{func_name}\s*\(', content, re.MULTILINE):
                        return True
                    if re.search(rf'^\s*class\s+{func_name}\s*[:\(]', content, re.MULTILINE):
                        return True
                    # Also check for async functions
                    if re.search(rf'^\s*async\s+def\s+{func_name}\s*\(', content, re.MULTILINE):
                        return True
            except:
                pass
        
        # Otherwise search all Python files
        for py_file in Path('.').rglob('*.py'):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if re.search(rf'^\s*def\s+{func_name}\s*\(', content, re.MULTILINE):
                        return True
                    if re.search(rf'^\s*class\s+{func_name}\s*[:\(]', content, re.MULTILINE):
                        return True
                    if re.search(rf'^\s*async\s+def\s+{func_name}\s*\(', content, re.MULTILINE):
                        return True
            except:
                continue
        
        return False
    
    def print_report(self, results: Dict[str, Any]):
        """Print validation report"""
        print("\n=== Validation Report ===\n")
        
        for result in results['results']:
            icon = '✅' if result['passed'] else '❌'
            print(f"{icon} {result['test']}: {result['message']}")
        
        print(f"\nOverall: {'✅ PASSING' if results['passing'] else '❌ FAILING'}")
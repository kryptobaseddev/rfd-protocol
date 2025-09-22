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
        modification_claims = self._extract_modification_claims(claims)
        
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
        
        # Check modification claims (critical for catching lies about updates)
        for mod_claim in modification_claims:
            verified = self._verify_modification_claim(mod_claim)
            validation_results.append({
                'type': 'modification',
                'target': mod_claim['target'],
                'exists': verified,
                'message': f"Modification {mod_claim['type']} in {mod_claim['target']}: {'VERIFIED' if verified else 'FABRICATED - AI LIED ABOUT MODIFICATION!'}"
            })
        
        # Overall pass/fail
        all_passed = all(r['exists'] for r in validation_results)
        return all_passed, validation_results
    
    def _extract_file_claims(self, text: str) -> List[str]:
        """Extract file paths mentioned in AI claims"""
        patterns = [
            # Match any file with an extension
            r'[cC]reated?\s+(?:file\s+)?([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'[wW]rote?\s+(?:to\s+)?([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'[fF]ile\s+([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'`([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)`',
            r'"([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)"',
            r"'([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)'",
            # Match modification patterns
            r'[uU]pdated?\s+([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'[mM]odified?\s+([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            r'[cC]hanged?\s+([a-zA-Z0-9_/\-\.]+\.[a-zA-Z0-9]+)',
            # Also match common files without extensions
            r'[cC]reated?\s+(Makefile|Dockerfile|Gemfile|Rakefile|Procfile)',
        ]
        
        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            files.update(matches)
        
        # Filter out obvious non-paths and common words
        filtered = []
        for f in files:
            # Skip common false positives
            if f in ['and', 'with', 'called', 'class', 'function', 'method']:
                continue
            if not f.startswith('http') and '://' not in f:
                filtered.append(f)
        
        return filtered
    
    def _extract_function_claims(self, text: str) -> List[Tuple[str, Optional[str]]]:
        """Extract function/class names mentioned in AI claims with improved accuracy"""
        # More specific and context-aware patterns
        patterns = [
            # High-confidence patterns (require specific context)
            r'(?:created|added|implemented|wrote|defined)\s+(?:a\s+|the\s+)?function\s+(?:called\s+|named\s+)?`?(\w+)`?',
            r'(?:created|added|implemented|wrote|defined)\s+(?:a\s+|the\s+)?class\s+(?:called\s+|named\s+)?`?(\w+)`?',
            r'(?:created|added|implemented|wrote|defined)\s+(?:a\s+|the\s+)?method\s+(?:called\s+|named\s+)?`?(\w+)`?',
            r'def\s+(\w+)\s*\(',  # Actual function definitions in code blocks
            r'class\s+(\w+)\s*[:\(]',  # Actual class definitions
            r'async\s+def\s+(\w+)\s*\(',  # Async function definitions
            
            # Medium-confidence patterns (require function/class keywords)
            r'function\s+`(\w+)\(\)`',  # Function with backticks and parentheses
            r'function\s+called\s+`?(\w+)`?',
            r'class\s+called\s+`?(\w+)`?',
            r'method\s+called\s+`?(\w+)`?',
            
            # Code block patterns
            r'```(?:python)?[\s\S]*?def\s+(\w+)\s*\(',
            r'```(?:python)?[\s\S]*?class\s+(\w+)\s*[:\(]',
            r'```(?:python)?[\s\S]*?async\s+def\s+(\w+)\s*\(',
            
            # Bullet point and list patterns (CRITICAL for catching test cases)
            r'[-*]\s+(\w+)\(\)',  # "- function_name()"
            r'[-*]\s+`?(\w+)\(\)`?',  # "- `function_name()`"
            r'[-*]\s+(\w+)\s*\(.*?\)',  # "- function_name(args)"
            
            # File modification patterns
            r'(?:updated|modified|changed)\s+.*?(?:with|to\s+include|adding)\s+.*?(\w+)\s*\(',
            r'(?:added|inserted)\s+.*?function\s+`?(\w+)`?',
            
            # Subtle modification patterns (CRITICAL for catching modification lies)
            r'(?:enhanced|improved|optimized|refactored)\s+(?:the\s+)?(?:existing\s+)?(\w+)\s+function',
            r'(?:enhanced|improved|optimized|refactored)\s+(?:the\s+)?(\w+)\s+(?:function|method)',
            r'(?:modified|updated|changed)\s+(?:the\s+)?(\w+)\s+(?:function|method)',
            r'(?:added|updated|modified)\s+.*?to\s+(\w+)\s*\(',
            r'function\s+(\w+)\s+(?:to|in|for)',  # "function hash_password to..."
        ]
        
        functions = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            functions.update(matches)
        
        # Enhanced filtering for false positives
        filtered_functions = set()
        common_false_positives = {
            'and', 'with', 'called', 'function', 'class', 'method', 'a', 'the', 'this', 'that',
            'it', 'is', 'was', 'will', 'can', 'could', 'should', 'would', 'new', 'old',
            'create', 'update', 'delete', 'get', 'set', 'main', 'test', 'run', 'start',
            'stop', 'end', 'file', 'name', 'type', 'data', 'value', 'key', 'id', 'user',
            'admin', 'login', 'logout', 'auth', 'api', 'app', 'web', 'server', 'client',
            'database', 'table', 'field', 'column', 'row', 'record', 'model', 'view',
            'controller', 'service', 'helper', 'util', 'config', 'setting', 'option',
            'param', 'arg', 'var', 'const', 'let', 'def', 'if', 'else', 'for', 'while',
            'try', 'catch', 'finally', 'return', 'yield', 'break', 'continue', 'pass'
        }
        
        for func in functions:
            func_lower = func.lower()
            # Skip common false positives
            if func_lower in common_false_positives:
                continue
            # Skip very short names (likely not real function names)
            if len(func) < 3:
                continue
            # Skip all uppercase (likely constants)
            if func.isupper() and len(func) > 1:
                continue
            # Skip obvious non-function patterns
            if func.isdigit() or not func.replace('_', '').isalnum():
                continue
            # Skip common English words that slip through
            if func_lower in {'have', 'been', 'done', 'made', 'used', 'like', 'just', 'only', 'also', 'even'}:
                continue
            
            filtered_functions.add(func)
        
        # Try to associate with file hints if mentioned nearby
        result = []
        for func in filtered_functions:
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
    
    def _extract_modification_claims(self, text: str) -> List[Dict[str, str]]:
        """Extract claims about modifying existing files"""
        modification_claims = []
        
        # Patterns for modification claims
        patterns = [
            r'(?:updated|modified|changed|edited)\s+([\w/\-\.]+\.\w+)\s+(?:to|with|by)\s+([^\n\.]+)',
            r'(?:added|inserted)\s+([^\n]+)\s+(?:to|into)\s+([\w/\-\.]+\.\w+)',
            r'(?:removed|deleted)\s+([^\n]+)\s+(?:from)\s+([\w/\-\.]+\.\w+)',
            r'in\s+([\w/\-\.]+\.\w+)[,:.]\s+(?:I\s+)?(?:added|updated|modified|changed)\s+([^\n\.]+)',
            
            # Enhanced/improved function patterns (CRITICAL for subtle lies)
            r'(?:enhanced|improved|optimized|refactored)\s+(?:the\s+)?(?:existing\s+)?\w+\s+function\s+in\s+([\w/\-\.]+\.\w+)\s+(?:to|:)\s*([^\n\.]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match) == 2:
                    # Standard format: (file_path, description)
                    first, second = match
                    if '.' in first and not '.' in second:  # first is likely file_path
                        file_path, change_desc = first, second
                    elif '.' in second and not '.' in first:  # second is likely file_path
                        change_desc, file_path = first, second
                    else:  # fallback: assume first is file_path
                        file_path, change_desc = first, second
                    
                    modification_claims.append({
                        'target': file_path.strip(),
                        'type': 'modification',
                        'description': change_desc.strip()
                    })
        
        return modification_claims
    
    def _verify_modification_claim(self, mod_claim: Dict[str, str]) -> bool:
        """Verify if a claimed modification actually exists"""
        file_path = mod_claim['target']
        description = mod_claim['description'].lower()
        
        # Check if file exists
        if not Path(file_path).exists():
            return False
        
        try:
            with open(file_path, 'r') as f:
                content = f.read().lower()
            
            # Look for evidence of the claimed modification
            # This is a basic implementation - could be enhanced with git diff analysis
            modification_keywords = ['function', 'class', 'def', 'import', 'from']
            
            for keyword in modification_keywords:
                if keyword in description:
                    # Look for the specific pattern in the file
                    if keyword == 'function' or keyword == 'def':
                        # Extract potential function name from description
                        func_match = re.search(r'\b(\w+)\s*\(', description)
                        if func_match:
                            func_name = func_match.group(1)
                            if re.search(rf'def\s+{func_name}\s*\(', content):
                                return True
                    elif keyword == 'class':
                        # Extract potential class name from description
                        class_match = re.search(r'class\s+(\w+)', description)
                        if class_match:
                            class_name = class_match.group(1)
                            if re.search(rf'class\s+{class_name}\s*[:\(]', content):
                                return True
                    elif keyword == 'import':
                        # Look for import statements
                        import_match = re.search(r'import\s+(\w+)', description)
                        if import_match:
                            import_name = import_match.group(1)
                            if f'import {import_name}' in content:
                                return True
            
            # If no specific patterns found, do a fuzzy search for key terms
            desc_words = [word for word in description.split() if len(word) > 3]
            matches = sum(1 for word in desc_words if word in content)
            return matches >= len(desc_words) * 0.5  # At least 50% of description words found
            
        except Exception:
            return False
    
    def print_report(self, results: Dict[str, Any]):
        """Print validation report"""
        print("\n=== Validation Report ===\n")
        
        for result in results['results']:
            icon = '✅' if result['passed'] else '❌'
            print(f"{icon} {result['test']}: {result['message']}")
        
        print(f"\nOverall: {'✅ PASSING' if results['passing'] else '❌ FAILING'}")
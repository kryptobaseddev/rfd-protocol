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
        Validate AI claims about file and function creation AND modifications.
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
        
        # Check modification claims - this is where we catch subtle lies
        for modification_type, target, details, file_hint in modification_claims:
            verified = self._verify_modification_claim(modification_type, target, details, file_hint)
            validation_results.append({
                'type': 'modification',
                'target': f"{target} ({modification_type})",
                'exists': verified,
                'message': f"Modification '{details}' to {target}: {'VERIFIED' if verified else 'NOT FOUND - AI HALLUCINATION!'}"
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
        """Extract function/class names mentioned in AI claims"""
        # Better patterns that avoid false positives
        patterns = [
            # Explicit function creation patterns
            r'[cC]reated\s+(?:function|method)\s+(?:called\s+)?(\w+)',  # "Created function foo" or "Created function called foo"
            r'[aA]dded\s+(?:function|method)\s+(?:called\s+)?(\w+)',    # "Added function foo"
            r'[iI]mplemented\s+(?:function|method)\s+(?:called\s+)?(\w+)',  # "Implemented function foo"
            r'[wW]rote\s+(?:function|method)\s+(?:called\s+)?(\w+)',    # "Wrote function foo"
            
            # Function definition patterns
            r'[fF]unction\s+called\s+(\w+)',  # "function called foo"
            r'[fF]unction\s+(\w+)',           # "function foo"
            r'[mM]ethod\s+(\w+)',             # "method foo"
            r'[dD]ef\s+(\w+)',                # "def foo"
            
            # Class creation patterns
            r'[cC]reated\s+(?:class)\s+(?:called\s+)?(\w+)',  # "Created class Foo"
            r'[aA]dded\s+(?:class)\s+(?:called\s+)?(\w+)',    # "Added class Foo"
            r'[iI]mplemented\s+(?:class)\s+(?:called\s+)?(\w+)',  # "Implemented class Foo"
            r'[cC]lass\s+(?:called\s+)?(\w+)',  # "class DataProcessor" or "class called DataProcessor"
            
            # Backtick patterns (code references)
            r'`(\w+)\(\)`',         # Function calls in backticks like `foo()`
            r'`def\s+(\w+)`',       # Function definitions in backticks like `def foo`
            r'`class\s+(\w+)`',     # Class definitions in backticks like `class Foo`
        ]
        
        functions = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            functions.update(matches)
        
        # Filter out common false positives and action words
        filtered_functions = set()
        false_positives = {
            'and', 'with', 'called', 'function', 'class', 'method', 'a', 'the', 'in', 'to', 'for',
            'created', 'added', 'implemented', 'wrote', 'def', 'async', 'return', 'returns',
            'error', 'handling', 'version', 'database', 'connection', 'init', 'self'
        }
        
        for func in functions:
            # Skip common words that aren't function names
            if func.lower() in false_positives:
                continue
            # Skip single letters
            if len(func) < 2:
                continue
            # Skip if starts with lowercase action words
            if func.lower().startswith(('add', 'created', 'implement', 'wrote')):
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
    
    def _extract_modification_claims(self, text: str) -> List[Tuple[str, str, str, Optional[str]]]:
        """
        Extract modification claims from AI text.
        Returns list of (modification_type, target, details, file_hint) tuples.
        """
        modification_claims = []
        
        # Patterns for different types of modifications
        patterns = [
            # Error handling additions
            (r'[aA]dded\s+error\s+handling\s+to\s+(\w+)', 'error_handling', 'added error handling'),
            (r'[aA]dded\s+try[/-]catch\s+(?:to\s+)?(\w+)', 'error_handling', 'added try-catch'),
            (r'[iI]mplemented\s+error\s+handling\s+(?:in\s+)?(\w+)', 'error_handling', 'implemented error handling'),
            
            # Async/await modifications  
            (r'[aA]dded\s+async\s+(?:version\s+of\s+)?(\w+)', 'async_conversion', 'made async'),
            (r'[iI]mplemented\s+async\s+(?:version\s+of\s+)?(\w+)', 'async_conversion', 'implemented async'),
            (r'[cC]onverted\s+(\w+)\s+to\s+async', 'async_conversion', 'converted to async'),
            
            # Database connections
            (r'[aA]dded\s+database\s+connection\s+to\s+(\w+)', 'database_integration', 'added database connection'),
            (r'[iI]mplemented\s+database\s+(?:integration\s+)?(?:in\s+)?(\w+)', 'database_integration', 'implemented database integration'),
            
            # Input validation
            (r'[aA]dded\s+(?:input\s+)?validation\s+to\s+(\w+)', 'input_validation', 'added input validation'),
            (r'[iI]mplemented\s+(?:input\s+)?validation\s+(?:in\s+)?(\w+)', 'input_validation', 'implemented input validation'),
            
            # Logging additions
            (r'[aA]dded\s+logging\s+to\s+(\w+)', 'logging', 'added logging'),
            (r'[iI]mplemented\s+logging\s+(?:in\s+)?(\w+)', 'logging', 'implemented logging'),
            
            # Performance optimizations
            (r'[oO]ptimized\s+(\w+)', 'optimization', 'optimized performance'),
            (r'[iI]mproved\s+performance\s+of\s+(\w+)', 'optimization', 'improved performance'),
            
            # General modifications
            (r'[mM]odified\s+(\w+)', 'general_modification', 'modified'),
            (r'[uU]pdated\s+(\w+)', 'general_modification', 'updated'),
            (r'[eE]nhanced\s+(\w+)', 'general_modification', 'enhanced'),
            (r'[iI]mproved\s+(\w+)', 'general_modification', 'improved'),
            
            # Bug fixes
            (r'[fF]ixed\s+(?:bug\s+in\s+)?(\w+)', 'bug_fix', 'fixed bug'),
            (r'[rR]esolved\s+(?:issue\s+in\s+)?(\w+)', 'bug_fix', 'resolved issue'),
        ]
        
        for pattern, mod_type, description in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Try to find file hint
                file_hint = self._find_file_hint_for_function(match, text)
                modification_claims.append((mod_type, match, description, file_hint))
        
        return modification_claims
    
    def _verify_modification_claim(self, modification_type: str, target: str, details: str, file_hint: Optional[str] = None) -> bool:
        """
        Verify if a claimed modification was actually made.
        This is conservative - for most modification types, we return False 
        unless we can definitively prove the modification exists.
        """
        
        # First, verify the target function/class exists
        if not self._verify_function_exists(target, file_hint):
            return False  # Can't modify what doesn't exist
        
        # Find the file containing the target
        target_file = None
        if file_hint and Path(file_hint).exists():
            target_file = file_hint
        else:
            # Search for the target in all Python files
            for py_file in Path('.').rglob('*.py'):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        if re.search(rf'^\s*def\s+{target}\s*\(', content, re.MULTILINE) or \
                           re.search(rf'^\s*class\s+{target}\s*[:\(]', content, re.MULTILINE) or \
                           re.search(rf'^\s*async\s+def\s+{target}\s*\(', content, re.MULTILINE):
                            target_file = str(py_file)
                            break
                except:
                    continue
        
        if not target_file:
            return False
        
        # Read the target file and analyze the function/class
        try:
            with open(target_file, 'r') as f:
                content = f.read()
            
            # Extract the function/class definition
            function_content = self._extract_function_content(content, target)
            if not function_content:
                return False
            
            # Check for specific modification types
            return self._verify_modification_type(modification_type, function_content, details)
            
        except Exception:
            return False
    
    def _extract_function_content(self, file_content: str, function_name: str) -> Optional[str]:
        """Extract the content of a specific function or class from file content"""
        lines = file_content.split('\n')
        
        # Find the function/class definition
        start_line = None
        for i, line in enumerate(lines):
            # Check for function definition
            if re.match(rf'^\s*def\s+{function_name}\s*\(', line) or \
               re.match(rf'^\s*async\s+def\s+{function_name}\s*\(', line) or \
               re.match(rf'^\s*class\s+{function_name}\s*[:\(]', line):
                start_line = i
                break
        
        if start_line is None:
            return None
        
        # Find the end of the function/class (next definition at same indentation level)
        start_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = len(lines)
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':  # Skip empty lines
                continue
            current_indent = len(line) - len(line.lstrip())
            # If we find a line at same or lower indentation that starts a definition, that's the end
            if current_indent <= start_indent and (line.strip().startswith('def ') or 
                                                  line.strip().startswith('class ') or
                                                  line.strip().startswith('async def ')):
                end_line = i
                break
        
        return '\n'.join(lines[start_line:end_line])
    
    def _verify_modification_type(self, modification_type: str, function_content: str, details: str) -> bool:
        """Verify if a specific type of modification exists in the function content"""
        
        if modification_type == 'error_handling':
            # Look for try/except blocks, error handling patterns
            has_try_except = 'try:' in function_content and 'except' in function_content
            # Be more strict - look for actual error handling code, not just keywords in comments
            has_raise = 'raise ' in function_content  # Actual raise statement
            has_exception_handling = 'except' in function_content and ':' in function_content
            has_assert = 'assert ' in function_content  # Actual assert statement
            
            return has_try_except or has_raise or has_exception_handling or has_assert
        
        elif modification_type == 'async_conversion':
            # Check if function is actually async
            return 'async def' in function_content or 'await' in function_content
        
        elif modification_type == 'database_integration':
            # Look for database-related code
            db_keywords = ['connect', 'cursor', 'execute', 'query', 'database', 'db', 'sql']
            return any(keyword in function_content.lower() for keyword in db_keywords)
        
        elif modification_type == 'input_validation':
            # Look for validation patterns
            validation_keywords = ['validate', 'check', 'assert', 'isinstance', 'type', 'len(']
            return any(keyword in function_content.lower() for keyword in validation_keywords)
        
        elif modification_type == 'logging':
            # Look for logging statements
            logging_keywords = ['log', 'print', 'debug', 'info', 'warning', 'error', 'logger']
            return any(keyword in function_content.lower() for keyword in logging_keywords)
        
        elif modification_type == 'optimization':
            # This is hard to verify automatically, so we're conservative
            # Look for common optimization patterns
            opt_keywords = ['cache', 'memo', 'optimization', 'efficient', 'fast']
            return any(keyword in function_content.lower() for keyword in opt_keywords)
        
        elif modification_type in ['general_modification', 'bug_fix']:
            # For general modifications, we can't really verify without knowing the original
            # This is conservative - we assume the AI might be lying unless we have clear evidence
            # In a real system, you'd compare against git history or previous versions
            return False  # Conservative approach - assume lying unless proven otherwise
        
        return False
    
    def print_report(self, results: Dict[str, Any]):
        """Print validation report"""
        print("\n=== Validation Report ===\n")
        
        for result in results['results']:
            icon = '✅' if result['passed'] else '❌'
            print(f"{icon} {result['test']}: {result['message']}")
        
        print(f"\nOverall: {'✅ PASSING' if results['passing'] else '❌ FAILING'}")
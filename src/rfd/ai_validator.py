"""
AI Claim Validation Module
Detects and validates AI claims about code creation and modifications
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class AIClaimValidator:
    """Validates AI claims about files and functions"""

    def __init__(self):
        pass

    def validate_ai_claims(self, claims: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate AI claims about file and function creation
        Returns (passed, details) tuple where details contains specific validation results
        """
        validation_results = []

        # Parse claims for file paths and function/class names
        file_claims = self._extract_file_claims(claims)
        function_claims = self._extract_function_claims(claims)
        modification_claims = self._extract_modification_claims(claims)

        # Check for vague/comprehensive claims that are often hallucinations
        vague_claims = self._detect_vague_claims(claims)
        for claim_text, claim_type, is_vague in vague_claims:
            if is_vague:
                validation_results.append(
                    {
                        "type": "vague_claim",
                        "claim": claim_text,
                        "valid": False,
                        "reason": f"Suspiciously vague {claim_type} claim - likely AI hallucination",
                    }
                )

        # Check each claimed file exists
        for file_path in file_claims:
            if not self._is_valid_file_path(file_path):
                continue

            exists = Path(file_path).exists()
            validation_results.append(
                {
                    "type": "file_claim",
                    "path": file_path,
                    "valid": exists,
                    "reason": ("File exists" if exists else "File does not exist - AI lied!"),
                }
            )

        # Check each claimed function/class exists in the files
        for func_name, file_hint in function_claims:
            # If a specific file was mentioned, we need strict verification
            if file_hint:
                # Strict check: function must be in the specific file mentioned AND file must exist
                try:
                    if Path(file_hint).exists():
                        found_in_file = self._check_function_in_file(func_name, file_hint)
                        validation_results.append(
                            {
                                "type": "function_claim",
                                "function": func_name,
                                "file": file_hint,
                                "valid": found_in_file,
                                "reason": f"Function {'found' if found_in_file else 'NOT FOUND'} in {file_hint}",
                            }
                        )
                    else:
                        validation_results.append(
                            {
                                "type": "function_claim",
                                "function": func_name,
                                "file": file_hint,
                                "valid": False,
                                "reason": f"Claimed file {file_hint} does not exist",
                            }
                        )
                except Exception:
                    validation_results.append(
                        {
                            "type": "function_claim",
                            "function": func_name,
                            "file": file_hint,
                            "valid": False,
                            "reason": f"Error checking {file_hint}",
                        }
                    )
            else:
                # General check: function exists somewhere in the codebase
                exists = self._verify_function_exists(func_name, file_hint)
                validation_results.append(
                    {
                        "type": "function_claim",
                        "function": func_name,
                        "valid": exists,
                        "reason": ("Function exists" if exists else "Function not found anywhere - AI lied!"),
                    }
                )

        # Check modification claims
        for target, mod_type, description, file_hint in modification_claims:
            valid = self._verify_modification_claim(target, mod_type, file_hint)
            validation_results.append(
                {
                    "type": "modification_claim",
                    "target": target,
                    "modification": description,
                    "valid": valid,
                    "reason": f"Modification {'verified' if valid else 'CANNOT VERIFY - likely false'}",
                }
            )

        # Overall validation passes if all claims are valid
        all_valid = all(result["valid"] for result in validation_results)

        return (all_valid, validation_results)

    def _extract_file_claims(self, text: str) -> List[str]:
        """Extract file paths mentioned in AI claims"""
        patterns = [
            # Match file creation/modification claims with file extensions
            # Order matters - jsx/tsx before js/ts to match more specific extensions first
            r"(?:Created|Modified|Updated|Added|Implemented|Fixed|Enhanced|Wrote|Made)\s+"
            r"(?:to\s+)?(?:file\s+)?([/\w.-]+\.(?:py|jsx|tsx|js|ts|go|rs|java|cpp|c|h|hpp|md|txt|yml|"
            r"yaml|json|xml|html|css|scss|sql|sh|bash))",
            # Match file creation/modification with descriptive text
            r"(?:Created|Modified|Updated|Added|Implemented|Fixed|Enhanced|Wrote|Made)\s+"
            r"(?:to\s+)?a?\s?(?:new\s+)?file\s+(?:called\s+|named\s+)?([/\w.-]+)",
            r"(?:In|At|File)\s+([/\w.-]+\.(?:py|js|ts|go|rs|java|cpp|c|h|hpp))",
            r"`([/\w.-]+\.(?:py|js|ts|jsx|tsx|go|rs|java|cpp|c|h|hpp))`",
            # Match quoted filenames
            r"['\"]([/\w.-]+\.(?:py|js|ts|jsx|tsx|go|rs|java|cpp|c|h|hpp|md|txt|yml|yaml|json))['\"]",
        ]

        files = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            files.update(matches)

        # Filter out common false positives
        filtered = []
        for f in files:
            # Skip if it's just an extension or too short
            if len(f) <= 3 or f.startswith("."):
                continue
            # Skip common words that might be matched
            if f in ["and", "with", "called", "class", "function", "method"]:
                continue
            if not f.startswith("http") and "://" not in f:
                filtered.append(f)
        return list(set(filtered))  # Remove duplicates

    def _extract_function_claims(self, text: str) -> List[Tuple[str, Optional[str]]]:
        """Extract function/class names mentioned in AI claims"""
        patterns = [
            # Explicit function creation patterns with async support
            r"[cC]reated\s+(?:async\s+)?(?:function|method)\s+(?:called\s+)?(\w+)",
            r"[cC]reated\s+(\w+)\s+(?:function|method)",
            r"[aA]dded\s+(?:async\s+)?(?:function|method)\s+(?:called\s+)?(\w+)",
            r"[aA]dded\s+(\w+)\s+(?:function|method)",
            r"[iI]mplemented\s+(?:async\s+)?(?:function|method)\s+(?:called\s+)?(\w+)",
            r"[iI]mplemented\s+(\w+)\s+(?:function|method)",
            r"[dD]efined\s+(?:async\s+)?(?:function|method)\s+(?:called\s+)?(\w+)",
            r"[dD]efined\s+(\w+)\s+(?:function|method)",
            r"[fF]unction\s+(?:called\s+)?(\w+)(?:\s|$)",
            # Class creation patterns
            r"[cC]reated\s+(?:class)\s+(?:called\s+)?(\w+)",
            r"[cC]reated\s+(\w+)\s+class",
            r"[aA]dded\s+(?:class)\s+(?:called\s+)?(\w+)",
            r"[aA]dded\s+(\w+)\s+class",
            r"[iI]mplemented\s+(?:class)\s+(?:called\s+)?(\w+)",
            r"[iI]mplemented\s+(\w+)\s+class",
            r"[iI]mplemented\s+(\w+)\s+model",
            r"[cC]lass\s+(?:called\s+)?(\w+)(?:\s|:|$)",
            # Backtick patterns (code references)
            r"`(\w+)\(\)`",
            r"`def\s+(\w+)`",
            r"`async\s+def\s+(\w+)`",
            r"`class\s+(\w+)`",
            r"`function\s+(\w+)`",
            r"`func\s+(\w+)`",
            # Actual code definitions (not just mentions)
            r"^\s*def\s+(\w+)\s*\(",
            r"^\s*async\s+def\s+(\w+)\s*\(",
            r"^\s*class\s+(\w+)\s*[:\(]",
        ]

        functions = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    func_name = match[0] if match[0] else match[1] if len(match) > 1 else None
                else:
                    func_name = match

                if func_name:
                    # Try to find associated file hint
                    file_hint = self._find_file_hint_for_function(func_name, text)
                    functions.add((func_name, file_hint))

        # Filter out common false positives
        filtered = []
        for func_name, file_hint in functions:
            # Skip very short names (likely false positives)
            if len(func_name) < 2:
                continue
            # Skip common words
            if func_name.lower() in [
                "and",
                "or",
                "if",
                "for",
                "while",
                "with",
                "as",
                "in",
                "to",
                "from",
                "class",
                "method",
                "a",
                "the",
                "in",
                "to",
                "of",
                "is",
                "are",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
            ]:
                continue
            filtered.append((func_name, file_hint))

        return filtered

    def _find_file_hint_for_function(self, func_name: str, text: str) -> Optional[str]:
        """Try to find if a specific file was mentioned for this function"""
        patterns = [
            rf"(?:in|to|at)\s+(?:file\s+)?([/\w.-]+\.py).*{func_name}",
            rf"{func_name}.*(?:in|to|at)\s+(?:file\s+)?([/\w.-]+\.py)",
            rf"([/\w.-]+\.py).*{func_name}",
            rf"{func_name}.*([/\w.-]+\.py)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the first valid file path
                for match in matches:
                    if self._is_valid_file_path(match):
                        return match
        return None

    def _is_valid_file_path(self, path: str) -> bool:
        """Check if a string looks like a valid file path"""
        if not path or len(path) < 3:
            return False
        if path.startswith("http"):
            return False
        if path in ["setup.py", "setup.cfg", "README.md"]:  # Common files
            return True
        if "/" in path or "\\" in path or path.endswith((".py", ".js", ".ts", ".go")):
            return True
        return False

    def _verify_function_exists(self, func_name: str, file_hint: Optional[str] = None) -> bool:
        """Verify if a function/class actually exists in the codebase"""
        if file_hint:
            try:
                if len(file_hint) <= 255 and Path(file_hint).exists():
                    if self._check_function_in_file(func_name, file_hint):
                        return True
            except Exception:
                pass

        # Search across all Python files
        for py_file in Path(".").glob("**/*.py"):
            # Skip virtual environments and common directories
            if any(part in {".venv", "venv", "__pycache__", ".git"} for part in py_file.parts):
                continue

            try:
                if self._check_function_in_file(func_name, str(py_file)):
                    return True
            except Exception:
                continue

        return False

    def _check_function_in_file(self, func_name: str, file_path: str) -> bool:
        """Check if a specific function/class exists in a file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Get file extension for language-specific patterns
            file_ext = Path(file_path).suffix.lower()

            # Language-specific patterns
            patterns = []

            # Python patterns
            if file_ext == ".py":
                patterns = [
                    rf"^\s*def\s+{func_name}\s*\(",
                    rf"^\s*async\s+def\s+{func_name}\s*\(",
                    rf"^\s*class\s+{func_name}\s*[:\(]",
                ]
            # JavaScript/TypeScript patterns
            elif file_ext in [".js", ".ts"]:
                patterns = [
                    rf"^\s*function\s+{func_name}\s*\(",
                    rf"^\s*async\s+function\s+{func_name}\s*\(",
                    rf"^\s*const\s+{func_name}\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=]+)\s*=>",
                    rf"^\s*(?:export\s+)?(?:default\s+)?class\s+{func_name}\s*{{",
                ]
            # Go patterns
            elif file_ext == ".go":
                patterns = [
                    rf"^\s*func\s+{func_name}\s*\(",
                    rf"^\s*func\s+\([^)]+\)\s+{func_name}\s*\(",
                    rf"^\s*type\s+{func_name}\s+struct\s*{{",
                ]
            # Rust patterns
            elif file_ext == ".rs":
                patterns = [
                    rf"^\s*(?:pub\s+)?(?:async\s+)?fn\s+{func_name}\s*[<\(]",
                    rf"^\s*(?:pub\s+)?struct\s+{func_name}\s*[{{<\s]",
                    rf"^\s*(?:pub\s+)?enum\s+{func_name}\s*[{{<\s]",
                ]
            else:
                # Generic patterns for other languages
                patterns = [
                    rf"\b{func_name}\s*\(",
                    rf"\bclass\s+{func_name}\b",
                    rf"\bfunction\s+{func_name}\b",
                ]

            # Check if any pattern matches
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE):
                    return True

            return False
        except Exception:
            return False

    def _extract_modification_claims(self, text: str) -> List[Tuple[str, str, str, Optional[str]]]:
        """Extract claims about modifications to existing code"""
        patterns = [
            # Error handling patterns
            (
                r"[aA]dded\s+error\s+handling\s+(?:to|for|in)\s+(\w+)",
                "error_handling",
                "added error handling",
            ),
            (
                r"[aA]dded\s+exception\s+handling\s+(?:to|for|in)\s+(\w+)",
                "error_handling",
                "added exception handling",
            ),
            # Logging patterns
            (
                r"[aA]dded\s+logging\s+(?:to|for|in)\s+(\w+)",
                "logging",
                "added logging",
            ),
            (
                r"[iI]mplemented\s+logging\s+(?:for|in)\s+(\w+)",
                "logging",
                "implemented logging",
            ),
            # Database integration
            (
                r"[aA]dded\s+database\s+connection\s+to\s+(\w+)",
                "database_connection",
                "added database connection",
            ),
            (
                r"[iI]ntegrated\s+(?:database\s+)?(?:with\s+)?(\w+)\s+with\s+(?:the\s+)?database",
                "database_integration",
                "integrated with database",
            ),
            # Validation patterns
            (
                r"[aA]dded\s+(?:input\s+)?validation\s+(?:to|for)\s+(\w+)",
                "input_validation",
                "added validation",
            ),
            # API endpoints
            (
                r"[cC]reated\s+(?:API\s+)?endpoint\s+(?:for\s+)?(\w+)",
                "api_endpoint",
                "created endpoint",
            ),
            (
                r"[aA]dded\s+(?:API\s+)?endpoint\s+(?:for\s+)?(\w+)",
                "api_endpoint",
                "added endpoint",
            ),
            # Authentication
            (
                r"[iI]mplemented\s+authentication\s+(?:for\s+)?(\w+)",
                "authentication",
                "implemented authentication",
            ),
            (
                r"[aA]dded\s+(?:JWT\s+)?token\s+validation\s+(?:to\s+)?(\w+)",
                "authentication",
                "added token validation",
            ),
            # Caching and performance
            (
                r"[aA]dded\s+caching\s+(?:to\s+)?(\w+)",
                "caching",
                "added caching",
            ),
            (
                r"[oO]ptimized\s+(?:the\s+)?(\w+)",
                "optimization",
                "optimized performance",
            ),
            # Async version claims
            (
                r"[iI]mplemented\s+async\s+version\s+of\s+(\w+)",
                "async_version",
                "implemented async version",
            ),
            (
                r"[cC]reated\s+async\s+version\s+of\s+(\w+)",
                "async_version",
                "created async version",
            ),
            (
                r"[cC]onverted\s+(\w+)\s+to\s+async",
                "async_version",
                "converted to async",
            ),
            # General modifications
            (r"[mM]odified\s+(\w+)", "general_modification", "modified"),
            (r"[uU]pdated\s+(\w+)", "general_modification", "updated"),
            (r"[eE]nhanced\s+(\w+)", "general_modification", "enhanced"),
            (r"[fF]ixed\s+(?:bug\s+in\s+)?(\w+)", "bug_fix", "fixed bug"),
        ]

        modifications = []
        for pattern, mod_type, description in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Try to find file hint
                file_hint = self._find_file_hint_for_function(match, text)
                modifications.append((match, mod_type, description, file_hint))

        return modifications

    def _detect_vague_claims(self, text: str) -> List[Tuple[str, str, bool]]:
        """Detect suspiciously vague or comprehensive claims that are often AI hallucinations"""
        vague_patterns = [
            (r"comprehensive\s+(?:test|testing)\s+suite", "testing", True),
            (r"robust\s+error\s+handling", "error_handling", True),
            (r"extensive\s+(?:test|testing|validation)", "testing", True),
            (r"production[- ]ready", "production", True),
            (r"enterprise[- ](?:grade|level)", "enterprise", True),
            (r"battle[- ]tested", "quality", True),
            (r"industry[- ]standard", "standard", True),
            (r"best\s+practices", "practices", True),
            (r"fully\s+(?:tested|validated|implemented)", "completeness", True),
            (r"complete\s+(?:implementation|solution)", "completeness", True),
            (r"end[- ]to[- ]end", "scope", True),
            (r"cutting[- ]edge", "technology", True),
            (r"state[- ]of[- ]the[- ]art", "technology", True),
            (r"blazing[- ]fast", "performance", True),
            (r"lightning[- ]fast", "performance", True),
            (r"highly\s+(?:optimized|performant|scalable)", "performance", True),
            (r"seamlessly\s+integrates", "integration", True),
            (r"perfectly\s+(?:handles|works|integrates)", "quality", True),
            (r"automatically\s+(?:handles|manages|detects)", "automation", True),
            (r"intelligently\s+(?:handles|manages|detects)", "intelligence", True),
            # More specific but still often false
            (r"added\s+comprehensive", "comprehensive", True),
            (r"implemented\s+full", "full", True),
            (r"created\s+complete", "complete", True),
        ]

        detected = []
        for pattern, claim_type, is_vague in vague_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    detected.append((match.group(0), claim_type, is_vague))

        return detected

    def _verify_modification_claim(self, target: str, modification_type: str, file_hint: Optional[str] = None) -> bool:
        """Verify if a claimed modification is likely true"""
        # First, verify the target function/class exists
        if not self._verify_function_exists(target, file_hint):
            return False  # Can't modify what doesn't exist

        # Find the file containing the target
        target_file = None
        if file_hint and Path(file_hint).exists():
            target_file = file_hint
        else:
            # Search for the file containing this function
            for py_file in Path(".").glob("**/*.py"):
                if any(part in {".venv", "venv", "__pycache__", ".git"} for part in py_file.parts):
                    continue

                try:
                    with open(py_file, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if (
                            re.search(rf"^\s*def\s+{target}\s*\(", content, re.MULTILINE)
                            or re.search(rf"^\s*class\s+{target}\s*[:\(]", content, re.MULTILINE)
                            or re.search(
                                rf"^\s*async\s+def\s+{target}\s*\(",
                                content,
                                re.MULTILINE,
                            )
                        ):
                            target_file = str(py_file)
                            break
                except Exception:
                    continue

        if not target_file:
            return False

        # Read the target file and analyze the function/class
        try:
            with open(target_file) as f:
                content = f.read()

            # Extract the function/class definition
            function_content = self._extract_function_content(content, target)
            if not function_content:
                return False

            # Check for specific modification types
            if modification_type == "error_handling":
                # Look for try/except or error handling patterns
                has_error_handling = any(
                    pattern in function_content for pattern in ["try:", "except ", "except:", "raise ", "finally:"]
                )
                return has_error_handling

            elif modification_type == "logging":
                # Must have actual logging imports and calls, not just print
                has_logging = "logger" in function_content or "logging" in function_content
                return has_logging

            elif modification_type == "input_validation":
                # Look for actual validation code
                validation_indicators = [
                    "isinstance(",
                    "type(",
                    "assert ",
                    "raise ValueError",
                    "raise TypeError",
                    ".isdigit(",
                    "len(",
                ]
                return any(ind in function_content for ind in validation_indicators)

            elif modification_type in ["database_integration", "database_connection"]:
                # Look for database-related code
                db_indicators = [
                    "cursor",
                    "execute",
                    "commit",
                    "rollback",
                    "query",
                    "SELECT",
                    "INSERT",
                    "UPDATE",
                    "DELETE",
                    "connection",
                    "connect(",
                    "db.",
                    "database",
                    "sql",
                ]
                return any(ind in function_content for ind in db_indicators)

            elif modification_type == "async_version":
                # Check if the function is actually async
                # The function_content should start with async def
                return "async def" in function_content or "async " in function_content[:100]

            elif modification_type in ["general_modification", "bug_fix"]:
                # For general modifications, we can't verify without original code
                # But we should return False to be conservative
                return False

            # Default to false for unknown modification types
            return False
        except Exception:
            return False

    def _extract_function_content(self, file_content: str, function_name: str) -> str:
        """Extract the content of a specific function or class from file content"""
        lines = file_content.split("\n")

        # Find the function/class definition
        start_line = None
        for i, line in enumerate(lines):
            # Check for function definition
            if (
                re.match(rf"^\s*def\s+{function_name}\s*\(", line)
                or re.match(rf"^\s*async\s+def\s+{function_name}\s*\(", line)
                or re.match(rf"^\s*class\s+{function_name}\s*[:\(]", line)
            ):
                start_line = i
                break

        if start_line is None:
            return ""

        # Find the end of the function/class (next definition at same indentation level)
        start_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = len(lines)

        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith("#"):
                continue
            # Check if we've reached another definition at the same or lower indentation
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= start_indent and (
                line.strip().startswith("def ")
                or line.strip().startswith("class ")
                or line.strip().startswith("async def ")
            ):
                end_line = i
                break

        # Extract the function content
        return "\n".join(lines[start_line:end_line])

    def detect_mock_data(self, file_path: str = None, content: str = None) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Detect mock data patterns in code
        Returns (has_mocks, details) where details contains specific mock findings
        """
        mock_findings = []

        # Get content to check
        if file_path and not content:
            if not Path(file_path).exists():
                return False, [{"type": "error", "message": f"File {file_path} not found"}]
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                return False, [{"type": "error", "message": f"Error reading file: {e}"}]

        if not content:
            return False, [{"type": "error", "message": "No content to check"}]

        # Common mock data patterns
        # Note: Using chr() to avoid self-detection in validation patterns
        mock_patterns = [
            # Test/fake data literals
            (r'["\']test[_\s]?user["\']', "test user data"),
            (
                r'["\']' + chr(102) + r'ake[_\s]?\w+["\']',
                chr(102) + "ake data",
            ),  # f-ake
            (
                r'["\']' + chr(100) + r'ummy[_\s]?\w+["\']',
                chr(100) + "ummy data",
            ),  # d-ummy
            (r'["\']example\.com["\']', "example.com domain"),
            (r'["\']foo@bar\.com["\']', "foo@bar email"),
            (r'["\']lorem\s+ipsum["\']', "lorem ipsum text"),
            (r'["\']123[- ]?456[- ]?7890["\']', "phone number pattern"),
            # Mock libraries and frameworks
            (r"from\s+unittest\.mock\s+import", "unittest mock import"),
            (r"import\s+mock", "mock module import"),
            (r"@mock\.", "mock decorator"),
            (r"MagicMock\s*\(", "MagicMock usage"),
            (r"Mock\s*\(", "Mock object usage"),
            (r"patch\s*\(", "patch usage"),
            # Hardcoded test values
            (r'password\s*=\s*["\']password["\']', "hardcoded test password"),
            (r'token\s*=\s*["\']test[_\s]?token["\']', "hardcoded test token"),
            (r'api[_\s]?key\s*=\s*["\']test[_\s]?key["\']', "hardcoded test API key"),
            # Mock functions/methods
            (r"def\s+mock_\w+", "mock function definition"),
            (
                r"def\s+" + chr(102) + r"ake_\w+",
                chr(102) + "ake function definition",
            ),  # f-ake
            (r"def\s+stub_\w+", "stub function definition"),
            (r"def\s+test_\w+", "test function definition"),
            # Mock return values
            (r'return\s+["\']mock[_\s]?\w+["\']', "mock return value"),
            (
                r'return\s+["\']' + chr(102) + r'ake[_\s]?\w+["\']',
                chr(102) + "ake return value",
            ),  # f-ake
            (r'return\s+\{\s*["\']test["\']', "test object return"),
            # Mock database records
            (r'INSERT\s+INTO.*["\']test_', "test database insert"),
            (r'VALUES.*["\']dummy', "dummy database values"),
            # Fixture and factory patterns
            (r"@pytest\.fixture", "pytest fixture"),
            (r"factory\.Faker\(", "Faker factory"),
            (r"FactoryBoy", "FactoryBoy usage"),
        ]

        # Check each pattern
        for pattern, description in mock_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Get line numbers for each match
                lines = content.split("\n")
                for match in matches:
                    line_num = None
                    for i, line in enumerate(lines, 1):
                        if match in line or (isinstance(match, str) and match.strip() in line):
                            line_num = i
                            mock_findings.append(
                                {
                                    "type": "mock_data",
                                    "pattern": description,
                                    "match": (match[:100] if len(str(match)) > 100 else str(match)),
                                    "line": line_num,
                                    "file": file_path or "provided content",
                                }
                            )
                            break

        # Check for test files (which are allowed to have mocks)
        is_test_file = False
        if file_path:
            is_test_file = any(part in str(file_path) for part in ["test_", "_test.py", "tests/", "test/"])

        # Filter findings if in test file
        if is_test_file:
            # In test files, only flag production mock usage
            mock_findings = [f for f in mock_findings if "import" not in f["pattern"] and "fixture" not in f["pattern"]]

        has_mocks = len(mock_findings) > 0

        return has_mocks, mock_findings

    def validate_no_mocks(self, directory: str = "src", exclude_tests: bool = True) -> Dict[str, Any]:
        """
        Validate that no mock data exists in production code
        Returns validation result with details
        """
        results = {
            "passing": True,
            "files_checked": 0,
            "files_with_mocks": [],
            "total_mock_instances": 0,
            "details": [],
        }

        # Get all Python files
        path = Path(directory)
        if not path.exists():
            return {"passing": False, "error": f"Directory {directory} not found"}

        for py_file in path.glob("**/*.py"):
            # Skip test files if requested
            if exclude_tests:
                if any(part in str(py_file) for part in ["test_", "_test.py", "tests/", "test/", "__pycache__"]):
                    continue

            # Skip the ai_validator.py file itself since it contains mock patterns for detection
            if "ai_validator.py" in str(py_file):
                continue

            results["files_checked"] += 1

            # Check for mocks in this file
            has_mocks, findings = self.detect_mock_data(str(py_file))

            if has_mocks:
                results["passing"] = False
                results["files_with_mocks"].append(str(py_file))
                results["total_mock_instances"] += len(findings)
                results["details"].extend(findings)

        return results

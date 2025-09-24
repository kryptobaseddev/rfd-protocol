"""
Build Engine for RFD
Handles compilation, setup, and build processes
"""

import subprocess
from typing import Any, Dict, Optional


class BuildEngine:
    def __init__(self, rfd):
        self.rfd = rfd
        self.spec = rfd.load_project_spec()
        self.stack = self.spec.get("stack", {})

    def get_status(self) -> Dict[str, Any]:
        """Get current build status"""
        # Check if service is running
        if self.stack.get("framework") == "fastapi":
            return self._check_fastapi()
        elif self.stack.get("framework") == "express":
            return self._check_express()
        # Add more frameworks

        return {"passing": False, "message": "Unknown stack"}
    
    def detect_stack(self) -> Dict[str, str]:
        """Detect the technology stack of the project"""
        from pathlib import Path
        
        stack = {}
        
        # Check for Python
        if Path("requirements.txt").exists() or Path("pyproject.toml").exists() or Path("setup.py").exists():
            stack["language"] = "python"
            if Path("manage.py").exists():
                stack["framework"] = "django"
            elif any(Path(".").glob("**/main.py")):
                # Check for FastAPI
                try:
                    if Path("requirements.txt").exists():
                        with open("requirements.txt") as f:
                            if "fastapi" in f.read():
                                stack["framework"] = "fastapi"
                except:
                    pass
            
            # Check pyproject.toml for dependencies
            if not stack.get("framework") and Path("pyproject.toml").exists():
                try:
                    with open("pyproject.toml") as f:
                        content = f.read()
                        if "fastapi" in content:
                            stack["framework"] = "fastapi"
                        elif "django" in content:
                            stack["framework"] = "django"
                        elif "flask" in content:
                            stack["framework"] = "flask"
                        elif "click" in content:
                            stack["framework"] = "click"
                except:
                    pass
        
        # Check for JavaScript
        elif Path("package.json").exists():
            stack["language"] = "javascript"
            try:
                import json
                with open("package.json") as f:
                    pkg = json.load(f)
                    deps = pkg.get("dependencies", {})
                    if "express" in deps:
                        stack["framework"] = "express"
                    elif "next" in deps:
                        stack["framework"] = "nextjs"
                    elif "react" in deps:
                        stack["framework"] = "react"
            except:
                pass
        
        # Check for Go
        elif Path("go.mod").exists():
            stack["language"] = "go"
        
        # Check for Rust
        elif Path("Cargo.toml").exists():
            stack["language"] = "rust"
        
        return stack

    def build_feature(self, feature_id: str) -> bool:
        """Build specific feature"""
        # Load feature spec
        feature = self._get_feature(feature_id)
        if not feature:
            print(f"❌ Feature {feature_id} not found")
            return False

        # Run stack-specific build
        if self.stack.get("language") == "python":
            return self._build_python(feature)
        elif self.stack.get("language") == "javascript":
            return self._build_javascript(feature)

        return False

    def _build_python(self, feature: Dict) -> bool:
        """Python-specific build process"""
        steps = [
            # Install dependencies
            (
                "Installing dependencies",
                ["uv", "pip", "install", "-r", "requirements.txt"],
            ),
            # Run formatters
            ("Formatting code", ["ruff", "format", "."]),
            # Run linters
            ("Linting", ["ruff", "check", ".rfd/"]),
            # Type checking
            ("Type checking", ["mypy", "."]),
            # Start service
            ("Starting service", self._get_start_command()),
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
        if self.stack.get("framework") == "fastapi":
            return [
                "uvicorn",
                "main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ]
        # Add more frameworks
        return []

    def _check_fastapi(self) -> Dict[str, Any]:
        """Check if FastAPI service is running"""
        try:
            import requests

            base_url = self.spec.get("api_contract", {}).get(
                "base_url", "http://localhost:8000"
            )
            health = self.spec.get("api_contract", {}).get("health_check", "/health")

            r = requests.get(f"{base_url}{health}", timeout=2)
            return {
                "passing": r.status_code == 200,
                "message": f"Service responding at {base_url}",
            }
        except Exception:
            return {"passing": False, "message": "Service not running"}

    def _get_feature(self, feature_id: str) -> Optional[Dict]:
        """Get feature from spec"""
        features = self.spec.get("features", [])
        for f in features:
            if f["id"] == feature_id:
                return f
        return None

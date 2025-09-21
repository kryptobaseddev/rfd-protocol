#!/usr/bin/env python3
"""
Universal Drop-in Test for RFD Protocol
Tests RFD with TypeScript, Python, Rust, and Go projects
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple

class UniversalRFDTest:
    """Test RFD works as drop-in tool for any language"""
    
    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="rfd_universal_"))
        self.rfd_source = Path("/mnt/projects/rfd-protocol/.rfd")
        self.results = {}
    
    def setup_test_project(self, lang: str, project_type: str) -> Path:
        """Create a test project for the specified language"""
        project_dir = self.test_dir / f"{lang}_project"
        project_dir.mkdir(parents=True)
        
        if lang == "typescript":
            self._create_typescript_project(project_dir, project_type)
        elif lang == "python":
            self._create_python_project(project_dir, project_type)
        elif lang == "rust":
            self._create_rust_project(project_dir, project_type)
        elif lang == "go":
            self._create_go_project(project_dir, project_type)
        
        # Copy RFD into the project
        shutil.copytree(self.rfd_source, project_dir / ".rfd")
        
        return project_dir
    
    def _create_typescript_project(self, project_dir: Path, project_type: str):
        """Create a TypeScript test project"""
        # package.json
        package_json = {
            "name": "test-ts-project",
            "version": "1.0.0",
            "scripts": {
                "build": "tsc",
                "test": "echo 'Tests pass'"
            },
            "devDependencies": {
                "typescript": "^5.0.0"
            }
        }
        (project_dir / "package.json").write_text(json.dumps(package_json, indent=2))
        
        # tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "outDir": "./dist"
            }
        }
        (project_dir / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))
        
        # Source files
        (project_dir / "src").mkdir()
        (project_dir / "src" / "index.ts").write_text("""
export class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }
    
    multiply(a: number, b: number): number {
        return a * b;
    }
}

export function greet(name: string): string {
    return `Hello, ${name}!`;
}
""")
        
        # RFD spec
        spec = {
            "version": "1.0",
            "language": "typescript",
            "framework": "node",
            "features": [
                {
                    "id": "calculator",
                    "description": "Basic calculator operations",
                    "status": "complete"
                },
                {
                    "id": "greeting",
                    "description": "Greeting function",
                    "status": "complete"
                }
            ],
            "claimed_files": [
                str(project_dir / "src" / "index.ts"),
                str(project_dir / "package.json"),
                str(project_dir / "tsconfig.json")
            ]
        }
        (project_dir / "rfd-spec.yaml").write_text(json.dumps(spec, indent=2))
    
    def _create_python_project(self, project_dir: Path, project_type: str):
        """Create a Python test project"""
        # requirements.txt
        (project_dir / "requirements.txt").write_text("pytest>=7.0.0\nflask>=2.0.0\n")
        
        # Main module
        (project_dir / "app.py").write_text("""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/users')
def get_users():
    return jsonify({"users": ["alice", "bob"]})

def calculate(x: int, y: int) -> int:
    return x + y

class DataProcessor:
    def process(self, data: list) -> dict:
        return {"count": len(data), "items": data}
""")
        
        # Test file
        (project_dir / "test_app.py").write_text("""
import pytest
from app import calculate, DataProcessor

def test_calculate():
    assert calculate(2, 3) == 5

def test_processor():
    proc = DataProcessor()
    result = proc.process([1, 2, 3])
    assert result["count"] == 3
""")
        
        # RFD spec
        spec = {
            "version": "1.0",
            "language": "python",
            "framework": "flask",
            "features": [
                {
                    "id": "api",
                    "description": "REST API endpoints",
                    "status": "complete"
                },
                {
                    "id": "data_processing",
                    "description": "Data processor class",
                    "status": "complete"
                }
            ],
            "claimed_files": [
                str(project_dir / "app.py"),
                str(project_dir / "test_app.py"),
                str(project_dir / "requirements.txt")
            ]
        }
        (project_dir / "rfd-spec.yaml").write_text(json.dumps(spec, indent=2))
    
    def _create_rust_project(self, project_dir: Path, project_type: str):
        """Create a Rust test project"""
        # Cargo.toml
        cargo_toml = """
[package]
name = "test-rust-project"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

[dev-dependencies]
"""
        (project_dir / "Cargo.toml").write_text(cargo_toml)
        
        # src/lib.rs
        (project_dir / "src").mkdir()
        (project_dir / "src" / "lib.rs").write_text("""
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct User {
    pub id: u32,
    pub name: String,
}

pub fn add(left: usize, right: usize) -> usize {
    left + right
}

pub fn create_user(id: u32, name: &str) -> User {
    User {
        id,
        name: name.to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }
    
    #[test]
    fn test_user() {
        let user = create_user(1, "Alice");
        assert_eq!(user.id, 1);
        assert_eq!(user.name, "Alice");
    }
}
""")
        
        # RFD spec
        spec = {
            "version": "1.0",
            "language": "rust",
            "framework": "cargo",
            "features": [
                {
                    "id": "user_model",
                    "description": "User data structure",
                    "status": "complete"
                },
                {
                    "id": "math_ops",
                    "description": "Basic math operations",
                    "status": "complete"
                }
            ],
            "claimed_files": [
                str(project_dir / "Cargo.toml"),
                str(project_dir / "src" / "lib.rs")
            ]
        }
        (project_dir / "rfd-spec.yaml").write_text(json.dumps(spec, indent=2))
    
    def _create_go_project(self, project_dir: Path, project_type: str):
        """Create a Go test project"""
        # go.mod
        (project_dir / "go.mod").write_text("""module test-go-project

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
)
""")
        
        # main.go
        (project_dir / "main.go").write_text("""package main

import (
    "fmt"
    "github.com/gin-gonic/gin"
)

type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

func Add(a, b int) int {
    return a + b
}

func CreateUser(id int, name string) User {
    return User{ID: id, Name: name}
}

func main() {
    r := gin.Default()
    
    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "healthy"})
    })
    
    r.GET("/users", func(c *gin.Context) {
        users := []User{
            CreateUser(1, "Alice"),
            CreateUser(2, "Bob"),
        }
        c.JSON(200, users)
    })
    
    fmt.Println("Server starting on :8080")
}
""")
        
        # main_test.go
        (project_dir / "main_test.go").write_text("""package main

import "testing"

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", result)
    }
}

func TestCreateUser(t *testing.T) {
    user := CreateUser(1, "Alice")
    if user.ID != 1 || user.Name != "Alice" {
        t.Errorf("CreateUser failed")
    }
}
""")
        
        # RFD spec
        spec = {
            "version": "1.0",
            "language": "go",
            "framework": "gin",
            "features": [
                {
                    "id": "web_server",
                    "description": "HTTP server with Gin",
                    "status": "complete"
                },
                {
                    "id": "user_management",
                    "description": "User struct and operations",
                    "status": "complete"
                }
            ],
            "claimed_files": [
                str(project_dir / "go.mod"),
                str(project_dir / "main.go"),
                str(project_dir / "main_test.go")
            ]
        }
        (project_dir / "rfd-spec.yaml").write_text(json.dumps(spec, indent=2))
    
    def test_rfd_commands(self, project_dir: Path, lang: str) -> Dict[str, Any]:
        """Test RFD commands in the project"""
        os.chdir(project_dir)
        results = {
            "language": lang,
            "project_dir": str(project_dir),
            "tests": {}
        }
        
        # Test RFD validation
        try:
            result = subprocess.run(
                ["python", ".rfd/rfd.py", "validate"],
                capture_output=True,
                text=True,
                timeout=10
            )
            results["tests"]["validate"] = {
                "passed": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            results["tests"]["validate"] = {
                "passed": False,
                "error": str(e)
            }
        
        # Test RFD check for AI hallucination
        ai_claim = f"I created {project_dir / 'fake_file.py'} with a function called fake_function"
        try:
            result = subprocess.run(
                ["python", ".rfd/rfd.py", "check", ai_claim],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Should detect this as false since file doesn't exist
            results["tests"]["hallucination_check"] = {
                "passed": "FALSE" in result.stdout or "HALLUCINATION" in result.stdout,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            results["tests"]["hallucination_check"] = {
                "passed": False,
                "error": str(e)
            }
        
        # Test RFD status
        try:
            result = subprocess.run(
                ["python", ".rfd/rfd.py", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            results["tests"]["status"] = {
                "passed": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            results["tests"]["status"] = {
                "passed": False,
                "error": str(e)
            }
        
        # Test session context (create and recall)
        try:
            # Create session context
            subprocess.run(
                ["python", ".rfd/rfd.py", "session", "set", "test_key", "test_value"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Recall session context
            result = subprocess.run(
                ["python", ".rfd/rfd.py", "session", "get", "test_key"],
                capture_output=True,
                text=True,
                timeout=5
            )
            results["tests"]["session_context"] = {
                "passed": "test_value" in result.stdout,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            results["tests"]["session_context"] = {
                "passed": False,
                "error": str(e)
            }
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run tests for all languages"""
        languages = [
            ("typescript", "web"),
            ("python", "api"),
            ("rust", "lib"),
            ("go", "service")
        ]
        
        for lang, project_type in languages:
            print(f"\n{'='*60}")
            print(f"Testing RFD with {lang.upper()} project...")
            print('='*60)
            
            # Setup project
            project_dir = self.setup_test_project(lang, project_type)
            
            # Run RFD tests
            results = self.test_rfd_commands(project_dir, lang)
            self.results[lang] = results
            
            # Print results
            self._print_language_results(lang, results)
        
        return self.results
    
    def _print_language_results(self, lang: str, results: Dict[str, Any]):
        """Print results for a language test"""
        print(f"\n{lang.upper()} Test Results:")
        print("-" * 40)
        
        all_passed = True
        for test_name, test_result in results["tests"].items():
            status = "✅ PASS" if test_result["passed"] else "❌ FAIL"
            print(f"  {test_name}: {status}")
            if not test_result["passed"]:
                all_passed = False
                if "error" in test_result and test_result["error"]:
                    print(f"    Error: {test_result['error'][:100]}")
        
        overall = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
        print(f"\n  Overall: {overall}")
    
    def print_final_summary(self):
        """Print final summary of all tests"""
        print(f"\n{'='*60}")
        print("FINAL SUMMARY - RFD Universal Drop-in Test")
        print('='*60)
        
        all_languages_passed = True
        for lang, results in self.results.items():
            lang_passed = all(test["passed"] for test in results["tests"].values())
            status = "✅" if lang_passed else "❌"
            print(f"{status} {lang.upper()}: {'PASSED' if lang_passed else 'FAILED'}")
            if not lang_passed:
                all_languages_passed = False
        
        print("\n" + "="*60)
        if all_languages_passed:
            print("✅ RFD WORKS AS UNIVERSAL DROP-IN TOOL!")
            print("   - Prevents AI hallucination (any language)")
            print("   - Works with TypeScript, Python, Rust, Go")
            print("   - Maintains session context")
            print("   - Production ready for solo developers")
        else:
            print("❌ RFD needs fixes for universal compatibility")
        print("="*60)
        
        return all_languages_passed
    
    def cleanup(self):
        """Clean up test directory"""
        try:
            shutil.rmtree(self.test_dir)
        except:
            pass

def main():
    """Run the universal drop-in test"""
    print("Starting RFD Universal Drop-in Test...")
    print("This will test RFD with TypeScript, Python, Rust, and Go projects")
    
    tester = UniversalRFDTest()
    
    try:
        tester.run_all_tests()
        success = tester.print_final_summary()
        
        # Return appropriate exit code
        sys.exit(0 if success else 1)
    
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
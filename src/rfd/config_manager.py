"""
Configuration management for RFD projects
Separates immutable config from dynamic state
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """Manages immutable project configuration in .rfd/config.yaml"""

    def __init__(self, rfd_dir: Path):
        self.rfd_dir = rfd_dir
        self.config_file = rfd_dir / "config.yaml"

    def create_config(
        self,
        name: str,
        description: str,
        language: str,
        framework: str,
        database: str,
        max_files: int = 50,
        max_loc: int = 1200,
        constraints: list = None,
    ) -> bool:
        """Create the immutable project configuration"""

        if self.config_file.exists():
            return False  # Config already exists, should be immutable

        config = {
            "project": {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "rfd_version": self._get_rfd_version(),
            },
            "stack": {"language": language, "framework": framework, "database": database},
            "rules": {
                "max_files": max_files,
                "max_loc_per_file": max_loc,
                "must_pass_tests": True,
                "no_mocks_in_prod": True,
            },
        }

        if constraints:
            config["constraints"] = constraints

        # Save to YAML
        self.rfd_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return True

    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load the immutable configuration"""
        if not self.config_file.exists():
            return None

        with open(self.config_file) as f:
            return yaml.safe_load(f)

    def get_stack(self) -> Optional[Dict[str, str]]:
        """Get just the stack configuration"""
        config = self.load_config()
        return config.get("stack") if config else None

    def get_rules(self) -> Optional[Dict[str, Any]]:
        """Get just the validation rules"""
        config = self.load_config()
        return config.get("rules") if config else None

    def get_constraints(self) -> Optional[list]:
        """Get project constraints"""
        config = self.load_config()
        return config.get("constraints", []) if config else []

    def is_configured(self) -> bool:
        """Check if project has been configured"""
        return self.config_file.exists()

    def _get_rfd_version(self) -> str:
        """Get the RFD version"""
        try:
            from . import __version__

            return __version__
        except ImportError:
            return "unknown"

    def migrate_from_project_md(self, project_md_path: Path) -> bool:
        """Migrate configuration from old PROJECT.md to config.yaml"""
        if self.config_file.exists():
            return False  # Already configured

        if not project_md_path.exists():
            return False

        # Parse PROJECT.md
        with open(project_md_path) as f:
            content = f.read()

        # Extract frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])

                # Extract static configuration
                config = {
                    "project": {
                        "name": frontmatter.get("name", "Unknown Project"),
                        "description": frontmatter.get("description", ""),
                        "created_at": datetime.now().isoformat(),
                        "rfd_version": self._get_rfd_version(),
                        "migrated_from": "PROJECT.md",
                    }
                }

                # Stack
                if "stack" in frontmatter:
                    config["stack"] = frontmatter["stack"]
                else:
                    # Try to detect from current setup
                    config["stack"] = {"language": "python", "framework": "click", "database": "sqlite"}

                # Rules
                if "rules" in frontmatter:
                    config["rules"] = frontmatter["rules"]
                else:
                    config["rules"] = {
                        "max_files": 50,
                        "max_loc_per_file": 1200,
                        "must_pass_tests": True,
                        "no_mocks_in_prod": True,
                    }

                # Constraints
                if "constraints" in frontmatter:
                    config["constraints"] = frontmatter["constraints"]

                # Save config
                self.rfd_dir.mkdir(parents=True, exist_ok=True)
                with open(self.config_file, "w") as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

                return True

        return False


class ProjectConfig:
    """
    Facade for accessing project configuration
    This replaces the need to parse PROJECT.md for config
    """

    def __init__(self, rfd_dir: Path):
        self.config_manager = ConfigManager(rfd_dir)
        self._config = None

    @property
    def config(self) -> Dict[str, Any]:
        """Lazy load configuration"""
        if self._config is None:
            self._config = self.config_manager.load_config() or {}
        return self._config

    @property
    def name(self) -> str:
        return self.config.get("project", {}).get("name", "Unknown Project")

    @property
    def description(self) -> str:
        return self.config.get("project", {}).get("description", "")

    @property
    def stack(self) -> Dict[str, str]:
        return self.config.get("stack", {})

    @property
    def language(self) -> str:
        return self.stack.get("language", "unknown")

    @property
    def framework(self) -> str:
        return self.stack.get("framework", "unknown")

    @property
    def database(self) -> str:
        return self.stack.get("database", "unknown")

    @property
    def rules(self) -> Dict[str, Any]:
        return self.config.get("rules", {})

    @property
    def max_files(self) -> int:
        return self.rules.get("max_files", 50)

    @property
    def max_loc_per_file(self) -> int:
        return self.rules.get("max_loc_per_file", 1200)

    @property
    def must_pass_tests(self) -> bool:
        return self.rules.get("must_pass_tests", True)

    @property
    def constraints(self) -> list:
        return self.config.get("constraints", [])

    def is_configured(self) -> bool:
        """Check if project is properly configured"""
        return self.config_manager.is_configured()

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return self.config

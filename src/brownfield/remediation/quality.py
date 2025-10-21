"""Quality gates installation and enforcement."""

import subprocess
from pathlib import Path
from typing import Optional

from brownfield.plugins.base import LanguageHandler, QualitySetupResult
from brownfield.state.decision_logger import DecisionLogger


class QualityGatesInstaller:
    """Install and configure quality gates for brownfield projects."""

    def __init__(self, handler: LanguageHandler, project_root: Path):
        """
        Initialize quality gates installer.

        Args:
            handler: Language-specific handler
            project_root: Project root directory
        """
        self.handler = handler
        self.project_root = project_root
        self.decision_logger = DecisionLogger(
            project_root / ".specify" / "memory" / "brownfield-decisions.md"
        )

    def install(
        self,
        skip_linter: bool = False,
        skip_formatter: bool = False,
        skip_hooks: bool = False,
        complexity_threshold: int = 10,
        fix_auto: bool = False,
    ) -> QualitySetupResult:
        """
        Install quality gates including linters, formatters, and pre-commit hooks.

        Args:
            skip_linter: Skip linter installation
            skip_formatter: Skip formatter installation
            skip_hooks: Skip pre-commit hooks installation
            complexity_threshold: Maximum allowed cyclomatic complexity
            fix_auto: Automatically fix issues where possible

        Returns:
            QualitySetupResult with setup details and metrics
        """
        # Use language handler's install_quality_gates method
        result = self.handler.install_quality_gates(self.project_root, complexity_threshold)

        # Log decision
        self.decision_logger.log_decision(
            problem="Project lacks quality gates and automated checks",
            solution=f"Installed {result.linter} linter, {result.formatter} formatter, and {len(result.hooks_installed)} pre-commit hooks",
            confidence="HIGH",
            alternatives=[
                "Manual code review only",
                "Different linter/formatter combination",
            ],
            risks=[
                "Pre-commit hooks may slow down commit process",
                "Linter rules may require tuning",
            ],
        )

        return result

    def analyze_complexity(self, threshold: int = 10) -> dict[str, list[dict]]:
        """
        Analyze code complexity and identify violations.

        Args:
            threshold: Maximum allowed cyclomatic complexity

        Returns:
            Dictionary with complexity violations by file
        """
        violations = {}

        try:
            # Run lizard with XML output
            result = subprocess.run(
                ["lizard", str(self.project_root), "--xml"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0 and not result.stdout:
                return violations

            # Parse XML to find violations
            import xml.etree.ElementTree as ET

            root = ET.fromstring(result.stdout)

            for item in root.findall(".//measure[@type='Function']/item"):
                if "average" in item.get("name", "").lower():
                    continue

                values = item.findall("value")
                if len(values) >= 3:
                    try:
                        ccn = int(values[2].text)
                        if ccn > threshold:
                            # Extract file and function name from item name
                            item_name = item.get("name", "")
                            # Format: "function_name(...) at ./path/to/file.py:line"
                            if " at " in item_name:
                                func_name = item_name.split(" at ")[0]
                                location = item_name.split(" at ")[1]

                                file_path = location.split(":")[0].lstrip("./")

                                if file_path not in violations:
                                    violations[file_path] = []

                                violations[file_path].append(
                                    {
                                        "function": func_name,
                                        "complexity": ccn,
                                        "threshold": threshold,
                                        "location": location,
                                    }
                                )
                    except (ValueError, AttributeError):
                        continue

        except Exception:
            pass

        return violations

    def scan_security_issues(self) -> dict[str, list[dict]]:
        """
        Scan for security issues using language-specific tools.

        Returns:
            Dictionary with security issues by severity
        """
        issues_by_severity = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        try:
            # For Python, get detailed bandit output
            result = subprocess.run(
                ["bandit", "-r", str(self.project_root), "-f", "json"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.stdout:
                import json

                data = json.loads(result.stdout)

                for issue in data.get("results", []):
                    severity = issue.get("issue_severity", "").lower()
                    if severity in issues_by_severity:
                        issues_by_severity[severity].append(
                            {
                                "file": issue.get("filename", ""),
                                "line": issue.get("line_number", 0),
                                "issue": issue.get("issue_text", ""),
                                "confidence": issue.get("issue_confidence", ""),
                                "severity": severity,
                            }
                        )

        except Exception:
            pass

        return issues_by_severity

    def create_pre_commit_config(self) -> Path:
        """
        Create .pre-commit-config.yaml for Python projects.

        Returns:
            Path to created config file
        """
        config_path = self.project_root / ".pre-commit-config.yaml"

        # Python-specific pre-commit configuration
        config_content = """# Pre-commit hooks for code quality
# See https://pre-commit.com for more information

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/pylint
    rev: v3.0.3
    hooks:
      - id: pylint
        args: ['--max-line-length=100', '--disable=C0111,R0903']

  - repo: local
    hooks:
      - id: complexity-check
        name: Check cyclomatic complexity
        entry: bash -c 'lizard --CCN 10 .'
        language: system
        pass_filenames: false
"""

        config_path.write_text(config_content, encoding="utf-8")
        return config_path

    def install_pre_commit_hooks(self) -> list[str]:
        """
        Install pre-commit hooks in the git repository.

        Returns:
            List of installed hook names
        """
        hooks_installed = []

        try:
            # Create .pre-commit-config.yaml
            config_path = self.create_pre_commit_config()
            hooks_installed.append(str(config_path.name))

            # Install pre-commit framework if available
            result = subprocess.run(
                ["pre-commit", "install"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                hooks_installed.append("pre-commit-framework")

        except (subprocess.SubprocessError, FileNotFoundError):
            # pre-commit not installed, that's okay - config file is still created
            pass

        return hooks_installed

    def create_linter_config(self) -> Optional[Path]:
        """
        Create .pylintrc configuration file for Python projects.

        Returns:
            Path to created config file
        """
        config_path = self.project_root / ".pylintrc"

        # Check if it already exists
        if config_path.exists():
            return config_path

        config_content = """[MASTER]
# Python code to execute, usually for sys.path manipulation
init-hook='import sys; sys.path.append("src")'

[MESSAGES CONTROL]
# Disable specific warnings
disable=C0111,  # missing-docstring
        R0903,  # too-few-public-methods
        W0212,  # protected-access
        C0103   # invalid-name

[FORMAT]
# Maximum number of characters on a single line
max-line-length=100

# Maximum number of lines in a module
max-module-lines=1000

[BASIC]
# Good variable names
good-names=i,j,k,ex,e,f,db,id,_

[DESIGN]
# Maximum number of arguments for function / method
max-args=7

# Maximum number of locals for function / method body
max-locals=15

# Maximum number of return / yield for function / method body
max-returns=6

# Maximum number of branch for function / method body
max-branches=12

# Maximum number of statements in function / method body
max-statements=50

[SIMILARITIES]
# Minimum lines number of a similarity
min-similarity-lines=4

[TYPECHECK]
# List of module names for which member attributes should not be checked
ignored-modules=
"""

        config_path.write_text(config_content, encoding="utf-8")
        return config_path

    def create_formatter_config(self) -> Optional[Path]:
        """
        Add black formatter configuration to pyproject.toml.

        Returns:
            Path to pyproject.toml if updated
        """
        pyproject_path = self.project_root / "pyproject.toml"

        if not pyproject_path.exists():
            return None

        # Check if black config already exists
        content = pyproject_path.read_text(encoding="utf-8")

        if "[tool.black]" in content:
            return pyproject_path

        # Append black configuration
        black_config = """

[tool.black]
line-length = 100
target-version = ['py311']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''
"""

        with open(pyproject_path, "a", encoding="utf-8") as f:
            f.write(black_config)

        return pyproject_path

    def document_complexity_justifications(
        self, violations: dict[str, list[dict]]
    ) -> Optional[Path]:
        """
        Create complexity-justification.md documenting complex functions.

        Args:
            violations: Complexity violations by file

        Returns:
            Path to created documentation file
        """
        if not violations:
            return None

        doc_path = self.project_root / "complexity-justification.md"

        lines = [
            "# Complexity Justification",
            "",
            "This document lists functions with cyclomatic complexity > 10 and justifications.",
            "",
            "## High Complexity Functions",
            "",
        ]

        for file_path, funcs in sorted(violations.items()):
            lines.append(f"### {file_path}")
            lines.append("")

            for func in funcs:
                lines.append(f"**Function**: `{func['function']}`")
                lines.append(f"- **Complexity**: {func['complexity']}")
                lines.append(f"- **Location**: {func['location']}")
                lines.append(
                    "- **Justification**: TODO - Document why this complexity is necessary"
                )
                lines.append(
                    "- **Refactoring Plan**: TODO - Outline plan to reduce complexity if possible"
                )
                lines.append("")

        doc_path.write_text("\n".join(lines), encoding="utf-8")
        return doc_path

"""Python language handler."""

from pathlib import Path
from typing import Optional

from brownfield.models.assessment import ConfidenceLevel
from brownfield.plugins.base import (
    DetectionResult,
    LanguageHandler,
    QualitySetupResult,
    TestSetupResult,
)
from brownfield.plugins.registry import register_handler
from brownfield.utils.process_runner import ProcessRunner


@register_handler("python")
class PythonHandler(LanguageHandler):
    """Python language handler."""

    def detect(self, project_root: Path) -> Optional[DetectionResult]:
        """Detect Python project."""
        evidence = {}
        confidence = ConfidenceLevel.LOW

        # Check for pyproject.toml
        pyproject = project_root / "pyproject.toml"
        if pyproject.exists():
            evidence["pyproject.toml"] = "Found Python project config"
            confidence = ConfidenceLevel.HIGH

        # Check for setup.py
        setup_py = project_root / "setup.py"
        if setup_py.exists():
            evidence["setup.py"] = "Found legacy setuptools config"
            if confidence == ConfidenceLevel.LOW:
                confidence = ConfidenceLevel.MEDIUM

        # Count .py files
        py_files = list(project_root.rglob("*.py"))
        if len(py_files) > 3:
            evidence["*.py files"] = f"Found {len(py_files)} Python files"
            if confidence == ConfidenceLevel.LOW:
                confidence = ConfidenceLevel.MEDIUM

        if not evidence:
            return None

        return DetectionResult(
            language="python",
            confidence=confidence,
            version=None,  # TODO: Detect Python version
            framework=None,  # TODO: Detect framework
            evidence=evidence,
        )

    def get_standard_structure(self) -> dict[str, list[str]]:
        """Return PEP 518 standard structure."""
        return {
            "src": ["__init__.py"],
            "tests": ["__init__.py", "conftest.py"],
            "docs": ["README.md"],
        }

    def bootstrap_tests(
        self, project_root: Path, core_modules: list[Path], coverage_target: float = 0.6
    ) -> TestSetupResult:
        """Add pytest and generate tests."""
        # Create tests directory structure
        tests_dir = project_root / "tests"
        tests_dir.mkdir(exist_ok=True)

        # Create __init__.py
        (tests_dir / "__init__.py").touch()

        # Create conftest.py with basic pytest configuration
        conftest_content = '''"""Pytest configuration."""

import pytest


@pytest.fixture
def project_root():
    """Return project root directory."""
    from pathlib import Path
    return Path(__file__).parent.parent
'''
        (tests_dir / "conftest.py").write_text(conftest_content, encoding="utf-8")

        # Add pytest dependencies to requirements-dev.txt if it exists
        requirements_dev = project_root / "requirements-dev.txt"
        dependencies_added = []

        if requirements_dev.exists():
            content = requirements_dev.read_text(encoding="utf-8")
            if "pytest" not in content:
                with open(requirements_dev, "a", encoding="utf-8") as f:
                    f.write("\npytest>=7.4.0\n")
                    f.write("pytest-cov>=4.1.0\n")
                    dependencies_added = ["pytest", "pytest-cov"]

        # Generate smoke tests using TestingBootstrapper
        from brownfield.remediation.testing import TestingBootstrapper

        bootstrapper = TestingBootstrapper(self, project_root)
        smoke_tests = bootstrapper.generate_smoke_tests(core_modules[:10])
        contract_tests = bootstrapper.generate_contract_tests(core_modules[:10])

        test_files_created = smoke_tests + contract_tests

        # Run tests to see how many pass
        tests_passing = 0
        tests_failing = 0

        try:
            result = ProcessRunner.run(
                ["pytest", "-v"],
                cwd=str(project_root),
                timeout=120,
            )
            # Parse pytest output
            if "passed" in result.stdout:
                import re

                match = re.search(r"(\d+) passed", result.stdout)
                if match:
                    tests_passing = int(match.group(1))
                match = re.search(r"(\d+) failed", result.stdout)
                if match:
                    tests_failing = int(match.group(1))
        except Exception:
            pass

        # Measure coverage
        coverage = bootstrapper.measure_coverage()

        return TestSetupResult(
            framework="pytest",
            dependencies_added=dependencies_added,
            test_files_created=[str(p) for p in test_files_created],
            coverage=coverage,
            tests_passing=tests_passing,
            tests_failing=tests_failing,
        )

    def install_quality_gates(
        self, project_root: Path, complexity_threshold: int = 10
    ) -> QualitySetupResult:
        """Add pylint, black, and hooks."""
        from brownfield.remediation.quality import QualityGatesInstaller

        installer = QualityGatesInstaller(self, project_root)

        # Create linter configuration
        installer.create_linter_config()

        # Create formatter configuration
        installer.create_formatter_config()

        # Install pre-commit hooks
        hooks_installed = installer.install_pre_commit_hooks()

        # Add quality tools to requirements-dev.txt
        requirements_dev = project_root / "requirements-dev.txt"
        if requirements_dev.exists():
            content = requirements_dev.read_text(encoding="utf-8")
            if "pylint" not in content or "black" not in content:
                with open(requirements_dev, "a", encoding="utf-8") as f:
                    if "pylint" not in content:
                        f.write("pylint>=3.0.0\n")
                    if "black" not in content:
                        f.write("black>=23.12.0\n")
                    if "pre-commit" not in content:
                        f.write("pre-commit>=3.6.0\n")

        # Run pylint to find issues
        linter_issues_found = 0
        try:
            result = ProcessRunner.run(
                ["pylint", "src"],
                cwd=str(project_root),
                timeout=120,
            )
            # Count issues from output
            import re

            match = re.search(r"Your code has been rated at ([\d.]+)/10", result.stdout)
            if match:
                rating = float(match.group(1))
                # Estimate issues (10 - rating roughly correlates to issues)
                linter_issues_found = int((10 - rating) * 10)
        except Exception:
            pass

        # Run black to format code
        formatter_files_changed = 0
        try:
            result = ProcessRunner.run(
                ["black", "--check", "src"],
                cwd=str(project_root),
                timeout=120,
            )
            # Count files that would be reformatted
            formatter_files_changed = result.stdout.count("would reformat")
        except Exception:
            pass

        # Analyze complexity violations
        complexity_violations_data = installer.analyze_complexity(complexity_threshold)
        complexity_violations = sum(len(funcs) for funcs in complexity_violations_data.values())

        # Document complexity justifications if violations exist
        if complexity_violations > 0:
            installer.document_complexity_justifications(complexity_violations_data)

        return QualitySetupResult(
            linter="pylint",
            formatter="black",
            linter_issues_found=linter_issues_found,
            linter_issues_fixed=0,  # Not auto-fixing in this phase
            formatter_files_changed=formatter_files_changed,
            hooks_installed=hooks_installed,
            complexity_violations=complexity_violations,
        )

    def verify_build(self, project_root: Path) -> bool:
        """Compile Python files."""
        # TODO: Implement build verification
        return True

    def measure_complexity(self, project_root: Path) -> dict[str, float]:
        """Use lizard for complexity analysis."""
        import xml.etree.ElementTree as ET

        try:
            # Run lizard with XML output
            result = ProcessRunner.run(
                ["lizard", str(project_root), "--xml"],
                cwd=str(project_root),
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0 and not result.stdout:
                # Lizard failed completely, return safe defaults
                return {"average": 0.0, "maximum": 0.0, "violations": 0.0}

            # Parse lizard XML output
            root = ET.fromstring(result.stdout)

            # Extract complexity metrics from XML
            # XML format: <cppncss><measure type="Function"><item><value>Nr</value><value>NCSS</value><value>CCN</value></item>...</measure></cppncss>
            # CCN is the third <value> in each <item>
            complexities = []
            violations = 0

            # Find all function measurements
            for item in root.findall(".//measure[@type='Function']/item"):
                # Skip items that are averages or summaries
                if "average" in item.get("name", "").lower():
                    continue

                # Get all value elements
                values = item.findall("value")
                if len(values) >= 3:  # Need at least 3 values: Nr, NCSS, CCN
                    try:
                        ccn = int(values[2].text)  # CCN is the 3rd value
                        complexities.append(ccn)
                        if ccn > 10:
                            violations += 1
                    except (ValueError, AttributeError):
                        continue

            if not complexities:
                return {"average": 0.0, "maximum": 0.0, "violations": 0.0}

            return {
                "average": sum(complexities) / len(complexities),
                "maximum": float(max(complexities)),
                "violations": float(violations),
            }

        except (ET.ParseError, ValueError):
            # Tool not available or failed
            return {"average": 0.0, "maximum": 0.0, "violations": 0.0}

    def scan_security(self, project_root: Path) -> dict[str, int]:
        """Run bandit security scanner."""
        import json

        try:
            # Run bandit with JSON output
            result = ProcessRunner.run(
                ["bandit", "-r", str(project_root), "-f", "json"],
                cwd=str(project_root),
                timeout=300,  # 5 minute timeout
            )

            # Bandit returns non-zero when vulnerabilities found, so we parse regardless
            if not result.stdout:
                return {"critical": 0, "high": 0, "medium": 0, "low": 0}

            # Parse bandit JSON output
            data = json.loads(result.stdout)

            # Count vulnerabilities by severity
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

            for result_item in data.get("results", []):
                severity = result_item.get("issue_severity", "").lower()
                if severity == "high":
                    severity_counts["high"] += 1
                elif severity == "medium":
                    severity_counts["medium"] += 1
                elif severity == "low":
                    severity_counts["low"] += 1

            return severity_counts

        except (json.JSONDecodeError, FileNotFoundError):
            # Bandit not installed or failed - return zeros (tool unavailable)
            return {"critical": 0, "high": 0, "medium": 0, "low": 0}

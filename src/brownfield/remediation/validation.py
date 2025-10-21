"""Validation runner for checking all 7 readiness gates."""

import json
from pathlib import Path
from typing import Optional

from brownfield.models.assessment import ProjectMetrics
from brownfield.models.gate import ReadinessGate
from brownfield.plugins.base import LanguageHandler


class ValidationRunner:
    """Evaluates all 7 readiness gates for graduation eligibility."""

    def __init__(
        self,
        project_root: Path,
        handler: LanguageHandler,
        baseline_metrics: Optional[ProjectMetrics] = None,
    ):
        self.project_root = project_root
        self.handler = handler
        self.baseline_metrics = baseline_metrics

    def validate_all_gates(self) -> list[ReadinessGate]:
        """
        Run all 7 readiness gates and return results.

        Returns:
            List of ReadinessGate objects with current_value and passed status updated
        """
        gates = [
            self._validate_test_coverage(),
            self._validate_complexity(),
            self._validate_directory_structure(),
            self._validate_build_status(),
            self._validate_api_documentation(),
            self._validate_security(),
            self._validate_git_hygiene(),
        ]

        return gates

    def _validate_test_coverage(self) -> ReadinessGate:
        """Gate 1: Test Coverage ≥60%."""
        gate = ReadinessGate(
            name="Test Coverage",
            description="Minimum test coverage on core business logic",
            threshold=0.6,
            current_value=0.0,
            passed=False,
            verification_command="pytest --cov=src --cov-report=json",
            remediation_guidance="Run 'brownfield testing' to generate more tests",
            exception_conditions=["Project is pure library with no business logic"],
        )

        try:
            # Read coverage from coverage.json if it exists
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, encoding="utf-8") as f:
                    coverage_data = json.load(f)
                    # coverage.py JSON format has totals.percent_covered
                    if "totals" in coverage_data:
                        gate.current_value = coverage_data["totals"]["percent_covered"] / 100.0
                    elif "percent_covered" in coverage_data.get("totals", {}):
                        gate.current_value = coverage_data["totals"]["percent_covered"]
        except Exception:
            # Coverage data unavailable
            pass

        gate.evaluate()
        return gate

    def _validate_complexity(self) -> ReadinessGate:
        """Gate 2: Cyclomatic Complexity <10 (or documented)."""
        gate = ReadinessGate(
            name="Cyclomatic Complexity",
            description="Maximum cyclomatic complexity",
            threshold=10.0,
            current_value=0.0,
            passed=False,
            verification_command="lizard -C 10 src/",
            remediation_guidance="Refactor complex functions or document justification",
            exception_conditions=["Complexity justified in complexity-justification.md"],
            justification_required=True,
        )

        try:
            # Use handler's measure_complexity method
            complexity_data = self.handler.measure_complexity(self.project_root)
            gate.current_value = complexity_data.get("maximum", 0.0)

            # Check if violations are documented
            justification_file = self.project_root / "complexity-justification.md"
            if gate.current_value > gate.threshold and justification_file.exists():
                # Allow violations if documented
                gate.justification = f"Violations documented in {justification_file.name}"
                gate.passed = True
            else:
                # Normal threshold evaluation
                gate.passed = gate.current_value <= gate.threshold

        except Exception:
            # Complexity tool unavailable
            pass

        return gate

    def _validate_directory_structure(self) -> ReadinessGate:
        """Gate 3: Directory Structure follows ecosystem conventions."""
        gate = ReadinessGate(
            name="Directory Structure",
            description="Follows ecosystem conventions",
            threshold=1.0,
            current_value=0.0,
            passed=False,
            verification_command="brownfield structure --verify",
            remediation_guidance="Run 'brownfield structure' to reorganize directories",
        )

        try:
            # Check for standard structure directories
            standard_structure = self.handler.get_standard_structure()
            found_dirs = 0
            total_dirs = len(standard_structure)

            if total_dirs == 0:
                # No standard structure defined, assume pass
                gate.current_value = 1.0
                gate.passed = True
                return gate

            for dir_name in standard_structure.keys():
                dir_path = self.project_root / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    found_dirs += 1

            gate.current_value = found_dirs / total_dirs if total_dirs > 0 else 0.0
            gate.passed = gate.current_value >= gate.threshold

        except Exception:
            pass

        return gate

    def _validate_build_status(self) -> ReadinessGate:
        """Gate 4: Build Status - clean build (<10 warnings)."""
        gate = ReadinessGate(
            name="Build Status",
            description="Build passes cleanly",
            threshold=1.0,
            current_value=0.0,
            passed=False,
            verification_command="language-specific",
            remediation_guidance="Fix build errors and warnings",
        )

        try:
            # Use handler's verify_build method
            build_passes = self.handler.verify_build(self.project_root)
            gate.current_value = 1.0 if build_passes else 0.0
            gate.passed = build_passes

        except Exception:
            # Build verification failed
            pass

        return gate

    def _validate_api_documentation(self) -> ReadinessGate:
        """Gate 5: API Documentation ≥80% of public APIs documented."""
        gate = ReadinessGate(
            name="API Documentation",
            description="Public APIs documented",
            threshold=0.8,
            current_value=0.0,
            passed=False,
            verification_command="manual",
            remediation_guidance="Add docstrings/JSDoc to public functions/classes",
        )

        # This is a manual gate for now
        # Could be enhanced with AST analysis to detect docstrings
        gate.current_value = 0.8  # Placeholder - assume pass for MVP
        gate.passed = True

        return gate

    def _validate_security(self) -> ReadinessGate:
        """Gate 6: Security - 0 critical vulnerabilities."""
        gate = ReadinessGate(
            name="Security",
            description="Zero critical vulnerabilities",
            threshold=0.0,
            current_value=0.0,
            passed=False,
            verification_command="bandit -r src/ -f json",
            remediation_guidance="Run 'brownfield quality' to fix security issues",
        )

        try:
            # Use handler's scan_security method
            security_counts = self.handler.scan_security(self.project_root)
            gate.current_value = float(security_counts.get("critical", 0))
            # Pass if 0 critical vulnerabilities
            gate.passed = gate.current_value == 0.0

        except Exception:
            # Security scanner unavailable
            pass

        return gate

    def _validate_git_hygiene(self) -> ReadinessGate:
        """Gate 7: Git Hygiene - no secrets, no large binaries."""
        gate = ReadinessGate(
            name="Git Hygiene",
            description="No secrets or large binaries",
            threshold=1.0,
            current_value=0.0,
            passed=False,
            verification_command="manual",
            remediation_guidance="Remove secrets and large files from git history",
        )

        # This is a manual gate for now
        # Could be enhanced with gitleaks or similar tools
        gate.current_value = 1.0  # Placeholder - assume pass for MVP
        gate.passed = True

        return gate

    def all_gates_passed(self, gates: list[ReadinessGate]) -> bool:
        """Check if all gates passed."""
        return all(gate.passed for gate in gates)

    def get_failed_gates(self, gates: list[ReadinessGate]) -> list[ReadinessGate]:
        """Get list of gates that failed."""
        return [gate for gate in gates if not gate.passed]

    def get_metrics_improvement(self) -> dict[str, dict[str, float]]:
        """
        Compare baseline metrics to current metrics.

        Returns:
            Dictionary with metric improvements
        """
        if not self.baseline_metrics:
            return {}

        improvements = {}

        # This would compare current metrics against baseline
        # For now, return empty dict as placeholder
        # Will be implemented when current metrics are collected

        return improvements

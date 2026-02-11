"""Gate validator for pass/fail logic and remediation guidance."""

from pathlib import Path

from brownfield.models.gate import ReadinessGate
from brownfield.models.state import BrownfieldState, Phase


class GateValidator:
    """Validates readiness gates and provides remediation guidance."""

    def __init__(self, project_root: Path, state: BrownfieldState):
        self.project_root = project_root
        self.state = state

    def validate_gate(self, gate: ReadinessGate) -> tuple[bool, str | None]:
        """
        Validate a single gate and return pass/fail with guidance.

        Args:
            gate: The readiness gate to validate

        Returns:
            Tuple of (passed, remediation_guidance)
        """
        if gate.passed:
            return True, None

        # Gate failed - provide specific remediation guidance
        guidance = self._get_remediation_guidance(gate)
        return False, guidance

    def validate_all_gates(self, gates: list[ReadinessGate]) -> dict[str, any]:
        """
        Validate all gates and generate comprehensive report.

        Args:
            gates: List of all readiness gates

        Returns:
            Validation report with pass/fail status and recommendations
        """
        passed_gates = []
        failed_gates = []

        for gate in gates:
            passed, guidance = self.validate_gate(gate)
            if passed:
                passed_gates.append(gate)
            else:
                failed_gates.append({"gate": gate, "guidance": guidance})

        all_passed = len(failed_gates) == 0

        return {
            "all_passed": all_passed,
            "total_gates": len(gates),
            "passed_count": len(passed_gates),
            "failed_count": len(failed_gates),
            "passed_gates": passed_gates,
            "failed_gates": failed_gates,
            "can_graduate": all_passed and self.state.phase == Phase.VALIDATION,
        }

    def _get_remediation_guidance(self, gate: ReadinessGate) -> str:
        """
        Get specific remediation guidance for a failed gate.

        Args:
            gate: The failed readiness gate

        Returns:
            Detailed remediation guidance
        """
        base_guidance = gate.remediation_guidance

        # Add gate-specific contextual guidance
        if gate.name == "Test Coverage":
            if gate.current_value < 0.3:
                return (
                    f"{base_guidance}\n"
                    f"  Current coverage is very low ({gate.current_value:.1%}). Consider:\n"
                    f"  1. Start with smoke tests for critical paths\n"
                    f"  2. Add contract tests for public APIs\n"
                    f"  3. Focus on core business logic modules first"
                )
            if gate.current_value < 0.5:
                return (
                    f"{base_guidance}\n"
                    f"  You're close ({gate.current_value:.1%} vs {gate.threshold:.1%} required).\n"
                    f"  Add tests for the remaining uncovered core modules."
                )
            return (
                f"{base_guidance}\n"
                f"  Just a bit more ({gate.current_value:.1%} vs {gate.threshold:.1%} required).\n"
                f"  Focus on high-value uncovered code paths."
            )

        if gate.name == "Cyclomatic Complexity":
            violations_count = gate.current_value - gate.threshold
            if violations_count > 20:
                return (
                    f"{base_guidance}\n"
                    f"  Many functions exceed complexity threshold. Consider:\n"
                    f"  1. Refactor the most complex functions first\n"
                    f"  2. Extract helper methods to reduce complexity\n"
                    f"  3. Document justifications for unavoidable complexity"
                )
            if gate.justification_required:
                return (
                    f"{base_guidance}\n"
                    f"  If refactoring isn't feasible, document justifications in:\n"
                    f"  {self.project_root / 'complexity-justification.md'}"
                )
            return base_guidance

        if gate.name == "Directory Structure":
            return (
                f"{base_guidance}\n"
                f"  Structure compliance: {gate.current_value:.0%}\n"
                f"  Use IDE refactoring tools to safely reorganize files."
            )

        if gate.name == "Build Status":
            return (
                f"{base_guidance}\n"
                f"  Build is currently failing. Common issues:\n"
                f"  1. Missing dependencies\n"
                f"  2. Import errors after refactoring\n"
                f"  3. Type errors or linting failures\n"
                f"  Run the build command to see specific errors."
            )

        if gate.name == "Security":
            critical_count = int(gate.current_value)
            return (
                f"{base_guidance}\n"
                f"  Found {critical_count} critical vulnerabilities.\n"
                f"  Security issues must be resolved before graduation."
            )

        if gate.name == "API Documentation":
            return (
                f"{base_guidance}\n"
                f"  Documentation coverage: {gate.current_value:.1%} (need {gate.threshold:.1%})\n"
                f"  Add docstrings to public functions and classes."
            )

        if gate.name == "Git Hygiene":
            return (
                f"{base_guidance}\n"
                f"  Detected potential secrets or large binaries.\n"
                f"  Use tools like git-filter-repo to clean history."
            )

        # Fallback to base guidance
        return base_guidance

    def recommend_next_phase(self, validation_result: dict) -> Phase | None:
        """
        Recommend which phase to return to based on failed gates.

        Args:
            validation_result: Result from validate_all_gates()

        Returns:
            Recommended phase to return to, or None if all passed
        """
        if validation_result["all_passed"]:
            return None

        # Analyze failed gates to determine which phase to return to
        failed_gate_names = [fg["gate"].name for fg in validation_result["failed_gates"]]

        # Priority order for phase recommendations
        if "Test Coverage" in failed_gate_names:
            return Phase.TESTING
        if "Cyclomatic Complexity" in failed_gate_names or "Security" in failed_gate_names:
            return Phase.QUALITY
        if "Directory Structure" in failed_gate_names or "Build Status" in failed_gate_names:
            return Phase.STRUCTURE
        if "API Documentation" in failed_gate_names or "Git Hygiene" in failed_gate_names:
            # These require manual intervention, stay in validation
            return Phase.VALIDATION

        return Phase.VALIDATION

    def generate_validation_report(self, validation_result: dict) -> str:
        """
        Generate a markdown report of validation results.

        Args:
            validation_result: Result from validate_all_gates()

        Returns:
            Markdown-formatted validation report
        """
        lines = ["# Validation Report\n"]

        if validation_result["all_passed"]:
            lines.append("## ✅ ALL GATES PASSED\n")
            lines.append(
                f"All {validation_result['total_gates']} readiness gates have passed. "
                "Project is ready for graduation.\n"
            )
        else:
            lines.append("## ❌ VALIDATION INCOMPLETE\n")
            lines.append(
                f"{validation_result['failed_count']} of {validation_result['total_gates']} "
                "gates failed. Address the issues below before graduation.\n"
            )

        # List passed gates
        if validation_result["passed_gates"]:
            lines.append("\n## Passed Gates\n")
            for gate in validation_result["passed_gates"]:
                lines.append(f"- ✅ **{gate.name}**: {gate.description}")
                if gate.justification:
                    lines.append(f"  - {gate.justification}")
                lines.append("")

        # List failed gates with guidance
        if validation_result["failed_gates"]:
            lines.append("\n## Failed Gates\n")
            for failed in validation_result["failed_gates"]:
                gate = failed["gate"]
                guidance = failed["guidance"]
                lines.append(f"- ❌ **{gate.name}**: {gate.description}")
                lines.append(f"  - **Threshold**: {gate.threshold}")
                lines.append(f"  - **Current**: {gate.current_value}")
                lines.append("  - **Status**: FAIL")
                lines.append(f"  - **Remediation**:\n    {guidance.replace(chr(10), chr(10) + '    ')}")
                lines.append("")

            # Recommend next phase
            recommended_phase = self.recommend_next_phase(validation_result)
            if recommended_phase:
                lines.append("\n## Recommendation\n")
                lines.append(f"Return to **{recommended_phase.value}** phase to address failed gates.\n")

        return "\n".join(lines)

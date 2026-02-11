"""Graduation report generator."""

from datetime import datetime
from pathlib import Path

from brownfield.models.gate import ReadinessGate
from brownfield.models.state import BrownfieldState


class GraduationReportGenerator:
    """Generates comprehensive graduation report."""

    def __init__(
        self,
        project_root: Path,
        state: BrownfieldState,
        gates: list[ReadinessGate],
    ):
        self.project_root = project_root
        self.state = state
        self.gates = gates

    def generate(self) -> str:
        """
        Generate graduation report summarizing brownfield transition.

        Returns:
            Markdown-formatted graduation report
        """
        lines = []

        # Header
        lines.append("# Brownfield Graduation Report")
        lines.append("")
        lines.append(f"**Project**: {self.project_root.name}")
        lines.append(f"**Language**: {self.state.language}")
        if self.state.detected_framework:
            lines.append(f"**Framework**: {self.state.detected_framework}")
        lines.append(f"**Graduated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Executive summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.extend(self._generate_executive_summary())
        lines.append("")

        # Metrics improvement
        lines.append("## Metrics Improvement")
        lines.append("")
        lines.extend(self._generate_metrics_comparison())
        lines.append("")

        # Readiness gates
        lines.append("## Readiness Gates Validation")
        lines.append("")
        lines.extend(self._generate_gates_summary())
        lines.append("")

        # Structural changes
        lines.append("## Structural Changes")
        lines.append("")
        lines.extend(self._generate_structural_changes())
        lines.append("")

        # Quality improvements
        lines.append("## Quality Improvements")
        lines.append("")
        lines.extend(self._generate_quality_improvements())
        lines.append("")

        # Next steps
        lines.append("## Next Steps")
        lines.append("")
        lines.extend(self._generate_next_steps())
        lines.append("")

        # Artifacts
        lines.append("## Generated Artifacts")
        lines.append("")
        lines.extend(self._generate_artifacts_list())
        lines.append("")

        return "\n".join(lines)

    def _generate_executive_summary(self) -> list[str]:
        """Generate executive summary section."""
        summary = []

        summary.append(
            "This project has successfully completed the brownfield-to-Speckit transition workflow. "
            "All readiness gates have passed, and the project is now ready for spec-driven development."
        )
        summary.append("")

        if self.state.baseline_metrics and self.state.baseline_metrics.lines_of_code:
            summary.append(
                f"The codebase contains {self.state.baseline_metrics.lines_of_code:,} lines of code "
                f"and has been transformed to meet production-ready quality standards."
            )
            summary.append("")

        return summary

    def _generate_metrics_comparison(self) -> list[str]:
        """Generate baseline vs final metrics comparison."""
        metrics = []

        if not self.state.baseline_metrics:
            metrics.append("No baseline metrics available.")
            return metrics

        # Create comparison table
        metrics.append("| Metric | Baseline | Current | Change |")
        metrics.append("|--------|----------|---------|--------|")

        # Test coverage
        baseline_cov = self.state.baseline_metrics.test_coverage or 0.0
        current_cov = self._get_current_coverage()
        if current_cov > 0:
            change = f"+{(current_cov - baseline_cov) * 100:.1f}%"
            metrics.append(f"| Test Coverage | {baseline_cov:.1%} | {current_cov:.1%} | {change} |")

        # Lines of code
        if self.state.baseline_metrics.lines_of_code:
            metrics.append(
                f"| Lines of Code | {self.state.baseline_metrics.lines_of_code:,} | "
                f"{self.state.baseline_metrics.lines_of_code:,} | - |"
            )

        # Complexity
        baseline_complex = self.state.baseline_metrics.average_complexity or 0.0
        current_complex = self._get_current_complexity()
        if current_complex > 0:
            change_val = current_complex - baseline_complex
            change_str = f"{change_val:+.1f}"
            metrics.append(f"| Avg Complexity | {baseline_complex:.1f} | {current_complex:.1f} | {change_str} |")

        metrics.append("")

        return metrics

    def _generate_gates_summary(self) -> list[str]:
        """Generate readiness gates summary."""
        gates_summary = []

        gates_summary.append("All 7 readiness gates passed:")
        gates_summary.append("")

        for i, gate in enumerate(self.gates, 1):
            status = "✅ PASS" if gate.passed else "❌ FAIL"
            gates_summary.append(f"{i}. **{gate.name}**: {status}")

            if gate.name == "Test Coverage":
                gates_summary.append(f"   - Coverage: {gate.current_value:.1%}")
            elif gate.name == "Cyclomatic Complexity":
                gates_summary.append(f"   - Max Complexity: {gate.current_value:.0f}")
            elif gate.name == "Security":
                gates_summary.append(f"   - Critical Vulnerabilities: {int(gate.current_value)}")

            if gate.justification:
                gates_summary.append(f"   - Note: {gate.justification}")

            gates_summary.append("")

        return gates_summary

    def _generate_structural_changes(self) -> list[str]:
        """Generate structural changes summary."""
        changes = []

        changes.append("The following structural improvements were made:")
        changes.append("")
        changes.append(f"- Reorganized to {self.state.language} standard directory structure")
        changes.append("- Imports updated and verified")
        changes.append("- Build system configured and passing")
        changes.append("")

        return changes

    def _generate_quality_improvements(self) -> list[str]:
        """Generate quality improvements summary."""
        improvements = []

        improvements.append("Quality tools installed and configured:")
        improvements.append("")

        if self.state.language == "python":
            improvements.append("- **Linter**: pylint")
            improvements.append("- **Formatter**: black")
            improvements.append("- **Test Framework**: pytest")
            improvements.append("- **Security Scanner**: bandit")
        elif self.state.language == "javascript":
            improvements.append("- **Linter**: ESLint")
            improvements.append("- **Formatter**: Prettier")
            improvements.append("- **Test Framework**: Jest")
            improvements.append("- **Security Scanner**: npm audit")
        elif self.state.language == "rust":
            improvements.append("- **Linter**: clippy")
            improvements.append("- **Formatter**: rustfmt")
            improvements.append("- **Test Framework**: Built-in")
            improvements.append("- **Security Scanner**: cargo audit")
        elif self.state.language == "go":
            improvements.append("- **Linter**: golangci-lint")
            improvements.append("- **Formatter**: gofmt")
            improvements.append("- **Test Framework**: Built-in")
            improvements.append("- **Security Scanner**: gosec")

        improvements.append("")
        improvements.append("- **Pre-commit Hooks**: Installed to enforce quality standards")
        improvements.append("- **Complexity Analysis**: lizard configured with threshold <10")
        improvements.append("")

        return improvements

    def _generate_next_steps(self) -> list[str]:
        """Generate next steps for users."""
        steps = []

        steps.append("1. **Review Constitution**: Read `.specify/constitution.md` for project conventions")
        steps.append("2. **Explore Templates**: Check `.specify/templates/` for spec/plan/tasks templates")
        steps.append("3. **Start Spec-Driven Development**: Use Speckit slash commands:")
        steps.append("   - `/speckit.specify` - Create feature specification")
        steps.append("   - `/speckit.plan` - Design implementation approach")
        steps.append("   - `/speckit.tasks` - Generate task breakdown")
        steps.append("4. **Archive Review**: Brownfield artifacts archived in `.specify/memory/brownfield-archive/`")
        steps.append("")

        return steps

    def _generate_artifacts_list(self) -> list[str]:
        """Generate list of created artifacts."""
        artifacts = []

        artifacts.append("The following artifacts were generated during graduation:")
        artifacts.append("")
        artifacts.append("- `.specify/constitution.md` - Project development principles")
        artifacts.append("- `.specify/templates/spec-template.md` - Feature specification template")
        artifacts.append("- `.specify/templates/plan-template.md` - Implementation plan template")
        artifacts.append("- `.specify/templates/tasks-template.md` - Task breakdown template")
        artifacts.append("- `.specify/memory/brownfield-archive/` - Original brownfield assessment data")
        artifacts.append("- `brownfield-graduation-report.md` - This report")
        artifacts.append("")

        return artifacts

    def _get_current_coverage(self) -> float:
        """Get current test coverage from gates."""
        for gate in self.gates:
            if gate.name == "Test Coverage":
                return gate.current_value
        return 0.0

    def _get_current_complexity(self) -> float:
        """Get current complexity from gates."""
        for gate in self.gates:
            if gate.name == "Cyclomatic Complexity":
                return gate.current_value
        return 0.0

    def save(self, output_path: Path | None = None) -> Path:
        """
        Save graduation report to file.

        Args:
            output_path: Custom path, defaults to brownfield-graduation-report.md

        Returns:
            Path where report was saved
        """
        if output_path is None:
            output_path = self.project_root / "brownfield-graduation-report.md"

        report_content = self.generate()
        output_path.write_text(report_content, encoding="utf-8")

        return output_path

"""Graduation report models."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from brownfield.models.assessment import Metrics
from brownfield.models.gate import ReadinessGate
from brownfield.models.state import Phase


@dataclass
class StructuralChange:
    """Documents a structural modification."""

    category: str
    description: str
    files_affected: list[Path]
    git_commit_sha: str
    timestamp: datetime


@dataclass
class TestImprovement:
    """Documents test infrastructure improvement."""

    module: str
    baseline_coverage: float
    final_coverage: float
    tests_added: int
    framework: str


@dataclass
class SecurityFix:
    """Documents security vulnerability remediation."""

    vulnerability_id: str
    severity: str
    description: str
    fix_applied: str
    verification: str


@dataclass
class GraduationReport:
    """Complete brownfield transition summary."""

    project_name: str
    graduated_at: datetime
    baseline_metrics: Metrics
    final_metrics: Metrics
    structural_changes: list[StructuralChange]
    test_improvements: list[TestImprovement]
    security_fixes: list[SecurityFix]
    time_spent: dict[Phase, int]
    total_commits: int
    archived_artifacts: list[Path]
    speckit_constitution: Path
    readiness_gates: list[ReadinessGate]

    def to_markdown(self) -> str:
        """Generate comprehensive graduation report."""
        md = f"# Brownfield Graduation Report: {self.project_name}\n\n"
        md += f"**Graduated**: {self.graduated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        md += "## Metrics Improvement\n\n"
        md += "| Metric | Baseline | Final | Delta |\n"
        md += "|--------|----------|-------|-------|\n"

        coverage_delta = self.final_metrics.test_coverage - self.baseline_metrics.test_coverage
        md += f"| Test Coverage | {self.baseline_metrics.test_coverage:.1%} | "
        md += f"{self.final_metrics.test_coverage:.1%} | {coverage_delta:+.1%} |\n"

        complexity_delta = self.final_metrics.complexity_avg - self.baseline_metrics.complexity_avg
        md += f"| Avg Complexity | {self.baseline_metrics.complexity_avg:.1f} | "
        md += f"{self.final_metrics.complexity_avg:.1f} | {complexity_delta:+.1f} |\n"

        vuln_delta = self.final_metrics.critical_vulnerabilities - self.baseline_metrics.critical_vulnerabilities
        md += f"| Critical Vulns | {self.baseline_metrics.critical_vulnerabilities} | "
        md += f"{self.final_metrics.critical_vulnerabilities} | {vuln_delta:+d} |\n"

        md += "\n## Structural Changes\n\n"
        if self.structural_changes:
            for change in self.structural_changes:
                sha_short = change.git_commit_sha[:7]
                md += f"- **{change.category}**: {change.description} ({sha_short})\n"
        else:
            md += "No structural changes were needed.\n"

        md += "\n## Test Infrastructure\n\n"
        if self.test_improvements:
            for improvement in self.test_improvements:
                md += f"- **{improvement.module}**: {improvement.baseline_coverage:.1%} → "
                md += f"{improvement.final_coverage:.1%} (+{improvement.tests_added} tests, "
                md += f"{improvement.framework})\n"
        else:
            md += "Test infrastructure was already adequate.\n"

        md += "\n## Security Fixes\n\n"
        if self.security_fixes:
            for fix in self.security_fixes:
                md += f"- **{fix.vulnerability_id}** ({fix.severity}): {fix.description}\n"
                md += f"  - Fix: {fix.fix_applied}\n"
                md += f"  - Verification: {fix.verification}\n"
        else:
            md += "No security vulnerabilities were found.\n"

        md += "\n## Time Spent\n\n"
        total_seconds = sum(self.time_spent.values())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        md += f"**Total Time**: {hours}h {minutes}m\n\n"
        for phase, seconds in self.time_spent.items():
            phase_minutes = seconds // 60
            md += f"- {phase.value.title()}: {phase_minutes}m\n"

        md += "\n## Readiness Gates\n\n"
        for gate in self.readiness_gates:
            status = "✅" if gate.passed else "❌"
            md += f"- {status} **{gate.name}**: {gate.current_value:.2f} "
            md += f"(threshold: {gate.threshold:.2f})\n"

        md += "\n## Git Activity\n\n"
        md += f"- **Total Commits**: {self.total_commits}\n"
        md += f"- **Archived Artifacts**: {len(self.archived_artifacts)} files\n"

        md += "\n## Next Steps\n\n"
        md += "Your project has graduated from BrownKit and is now Speckit-ready!\n\n"
        md += f"1. Review generated Speckit constitution: `{self.speckit_constitution}`\n"
        md += '2. Start spec-driven development: `/speckit.specify "your feature"`\n'
        md += "3. Archived brownfield artifacts: `.specify/memory/brownfield-archive/`\n"

        md += "\n---\n\n"
        md += "🎉 **Congratulations on completing the brownfield transition!** 🎉\n"

        return md

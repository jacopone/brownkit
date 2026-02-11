"""Assessment data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class ConfidenceLevel(Enum):
    """Detection confidence levels."""

    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5


@dataclass
class LanguageDetection:
    """Language and framework detection results."""

    language: str
    confidence: ConfidenceLevel
    version: str | None
    framework: str | None
    secondary_languages: list[tuple[str, float]] = field(default_factory=list)
    detection_evidence: dict[str, str] = field(default_factory=dict)


@dataclass
class ComplexityViolation:
    """Single complexity violation."""

    file: str
    function: str
    complexity: int
    line: int


@dataclass
class Metrics:
    """Quantitative codebase metrics."""

    test_coverage: float  # 0.0-1.0
    complexity_avg: float
    complexity_max: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    build_status: str  # "passing" | "failing" | "unknown"
    documentation_coverage: float
    total_loc: int
    test_loc: int
    git_commits: int
    git_secrets_found: int
    complexity_violations: list[ComplexityViolation] = field(default_factory=list)


@dataclass
class TechDebtCategory:
    """Tech debt in a specific category."""

    category: str
    severity: str
    issues: list[str]
    estimated_remediation_time: str


@dataclass
class AssessmentReport:
    """Complete codebase assessment report."""

    project_name: str
    project_root: Path
    assessed_at: datetime
    agent_version: str
    language_detection: LanguageDetection
    baseline_metrics: Metrics
    tech_debt: list[TechDebtCategory]
    assumptions: list[str]
    limitations: list[str]
    risk_assessment: str
    analysis_mode: str
    analysis_duration_seconds: int

    def to_markdown(self) -> str:
        """Generate Markdown report for human consumption."""
        md = f"# Assessment Report: {self.project_name}\n\n"
        md += f"**Assessed**: {self.assessed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Agent Version**: {self.agent_version}\n"
        md += f"**Analysis Mode**: {self.analysis_mode}\n"
        md += f"**Duration**: {self.analysis_duration_seconds}s\n\n"

        md += "## Language Detection\n\n"
        md += f"- **Primary Language**: {self.language_detection.language}\n"
        md += f"- **Confidence**: {self.language_detection.confidence.name}\n"
        if self.language_detection.version:
            md += f"- **Version**: {self.language_detection.version}\n"
        if self.language_detection.framework:
            md += f"- **Framework**: {self.language_detection.framework}\n"

        if self.language_detection.secondary_languages:
            md += "\n**Secondary Languages**:\n"
            for lang, conf in self.language_detection.secondary_languages:
                md += f"- {lang} ({conf:.0%} confidence)\n"

        md += "\n**Detection Evidence**:\n"
        for file, reason in self.language_detection.detection_evidence.items():
            md += f"- `{file}`: {reason}\n"

        md += "\n## Baseline Metrics\n\n"
        md += "| Metric | Value |\n"
        md += "|--------|-------|\n"
        md += f"| Test Coverage | {self.baseline_metrics.test_coverage:.1%} |\n"
        md += f"| Avg Complexity | {self.baseline_metrics.complexity_avg:.1f} |\n"
        md += f"| Max Complexity | {self.baseline_metrics.complexity_max} |\n"
        md += f"| Critical Vulnerabilities | {self.baseline_metrics.critical_vulnerabilities} |\n"
        md += f"| High Vulnerabilities | {self.baseline_metrics.high_vulnerabilities} |\n"
        md += f"| Medium Vulnerabilities | {self.baseline_metrics.medium_vulnerabilities} |\n"
        md += f"| Build Status | {self.baseline_metrics.build_status} |\n"
        md += f"| Documentation Coverage | {self.baseline_metrics.documentation_coverage:.1%} |\n"
        md += f"| Total LOC | {self.baseline_metrics.total_loc:,} |\n"
        md += f"| Test LOC | {self.baseline_metrics.test_loc:,} |\n"
        md += f"| Git Commits | {self.baseline_metrics.git_commits} |\n"
        md += f"| Git Secrets Found | {self.baseline_metrics.git_secrets_found} |\n"

        # Add complexity violations section if any exist
        if self.baseline_metrics.complexity_violations:
            md += "\n## Complexity Violations\n\n"
            md += f"Found {len(self.baseline_metrics.complexity_violations)} functions with complexity > 10:\n\n"
            md += "| File | Function | Complexity | Line |\n"
            md += "|------|----------|------------|------|\n"
            for v in self.baseline_metrics.complexity_violations[:10]:  # Show top 10
                md += f"| {v.file} | `{v.function}` | {v.complexity} | {v.line} |\n"
            if len(self.baseline_metrics.complexity_violations) > 10:
                md += f"\n*...and {len(self.baseline_metrics.complexity_violations) - 10} more violations*\n"
            md += "\n"

        md += "## Tech Debt Categories\n\n"
        for debt in self.tech_debt:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(debt.severity.lower(), "⚪")
            md += f"### {severity_emoji} {debt.severity.upper()} - {debt.category.title()}\n\n"
            md += f"**Estimated Remediation**: {debt.estimated_remediation_time}\n\n"
            md += "**Issues**:\n"
            for issue in debt.issues:
                md += f"- {issue}\n"
            md += "\n"

        md += "## Assumptions\n\n"
        for assumption in self.assumptions:
            md += f"- {assumption}\n"

        md += "\n## Analysis Limitations\n\n"
        for limitation in self.limitations:
            md += f"- {limitation}\n"

        md += f"\n## Risk Assessment\n\n{self.risk_assessment}\n"

        return md

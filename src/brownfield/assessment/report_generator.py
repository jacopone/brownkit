"""Assessment report generation."""

from datetime import datetime
from pathlib import Path

from brownfield.models.assessment import (
    AssessmentReport,
    LanguageDetection,
    Metrics,
    TechDebtCategory,
)


class ReportGenerator:
    """Generates assessment reports."""

    def generate(
        self,
        project_name: str,
        project_root: Path,
        language_detection: LanguageDetection,
        baseline_metrics: Metrics,
        tech_debt: list[TechDebtCategory],
        analysis_mode: str,
        duration_seconds: int,
    ) -> AssessmentReport:
        """Generate assessment report."""
        return AssessmentReport(
            project_name=project_name,
            project_root=project_root,
            assessed_at=datetime.utcnow(),
            agent_version="0.1.0",
            language_detection=language_detection,
            baseline_metrics=baseline_metrics,
            tech_debt=tech_debt,
            assumptions=["Project follows standard conventions"],
            limitations=["Cannot analyze without language tools installed"],
            risk_assessment="Medium risk for automated remediation",
            analysis_mode=analysis_mode,
            analysis_duration_seconds=duration_seconds,
        )

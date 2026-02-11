"""Report generation for assessment and graduation."""

from pathlib import Path

from brownfield.models.assessment import AssessmentReport
from brownfield.models.report import GraduationReport


class ReportWriter:
    """Generates Markdown reports."""

    @staticmethod
    def write_assessment_report(report: AssessmentReport, output_path: Path) -> None:
        """Write assessment report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())

    @staticmethod
    def write_graduation_report(report: GraduationReport, output_path: Path) -> None:
        """Write graduation report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())

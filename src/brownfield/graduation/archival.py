"""Artifact archival for brownfield graduation."""

import shutil
from datetime import datetime
from pathlib import Path


class ArtifactArchiver:
    """Archives brownfield artifacts after graduation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def archive_all(self, archive_path: Path | None = None) -> dict[str, Path]:
        """
        Archive all brownfield artifacts to specified location.

        Args:
            archive_path: Custom archive location, defaults to .specify/memory/brownfield-archive/

        Returns:
            Dictionary mapping artifact type to archived path
        """
        if archive_path is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            archive_path = self.project_root / ".specify" / "memory" / "brownfield-archive" / timestamp

        archive_path.mkdir(parents=True, exist_ok=True)

        archived = {}

        # Archive brownfield state
        state_file = self.project_root / ".brownfield" / "state.json"
        if state_file.exists():
            archived_state = archive_path / "state.json"
            shutil.copy2(state_file, archived_state)
            archived["state"] = archived_state

        # Archive assessment report if it exists
        assessment_report = self.project_root / "brownfield-assessment-report.md"
        if assessment_report.exists():
            archived_assessment = archive_path / "assessment-report.md"
            shutil.copy2(assessment_report, archived_assessment)
            archived["assessment"] = archived_assessment

        # Archive structure plan if it exists
        structure_plan = self.project_root / "structure-plan.md"
        if structure_plan.exists():
            archived_plan = archive_path / "structure-plan.md"
            shutil.copy2(structure_plan, archived_plan)
            archived["structure_plan"] = archived_plan

        # Archive structure verification if it exists
        structure_verification = self.project_root / "structure-verification.md"
        if structure_verification.exists():
            archived_verification = archive_path / "structure-verification.md"
            shutil.copy2(structure_verification, archived_verification)
            archived["structure_verification"] = archived_verification

        # Archive complexity justification if it exists
        complexity_justification = self.project_root / "complexity-justification.md"
        if complexity_justification.exists():
            archived_complexity = archive_path / "complexity-justification.md"
            shutil.copy2(complexity_justification, archived_complexity)
            archived["complexity_justification"] = archived_complexity

        # Archive coverage data if it exists
        coverage_json = self.project_root / "coverage.json"
        if coverage_json.exists():
            archived_coverage = archive_path / "coverage.json"
            shutil.copy2(coverage_json, archived_coverage)
            archived["coverage"] = archived_coverage

        # Create archive manifest
        manifest_path = archive_path / "MANIFEST.md"
        manifest_content = self._generate_manifest(archived)
        manifest_path.write_text(manifest_content, encoding="utf-8")
        archived["manifest"] = manifest_path

        return archived

    def _generate_manifest(self, archived_files: dict[str, Path]) -> str:
        """Generate manifest listing all archived files."""
        lines = []

        lines.append("# Brownfield Archive Manifest")
        lines.append("")
        lines.append(f"**Archived**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("## Archived Files")
        lines.append("")

        for artifact_type, path in archived_files.items():
            if artifact_type != "manifest":  # Don't list the manifest itself
                lines.append(f"- **{artifact_type}**: `{path.name}`")

        lines.append("")
        lines.append("## Purpose")
        lines.append("")
        lines.append(
            "These files document the brownfield assessment and transition process. "
            "They are archived for future reference and audit purposes."
        )
        lines.append("")

        lines.append("## Restoration")
        lines.append("")
        lines.append("To restore brownfield state (e.g., for re-entry after quality regression):")
        lines.append("1. Copy `state.json` to `.brownfield/state.json`")
        lines.append("2. Run `brownfield status` to verify state")
        lines.append("")

        return "\n".join(lines)

    def cleanup_brownfield_files(self) -> list[Path]:
        """
        Remove brownfield working files from project root after archival.

        Returns:
            List of removed file paths
        """
        removed = []

        files_to_remove = [
            "brownfield-assessment-report.md",
            "structure-plan.md",
            "structure-verification.md",
            # Keep complexity-justification.md - it's still relevant
            # Keep coverage.json - used by test framework
        ]

        for filename in files_to_remove:
            file_path = self.project_root / filename
            if file_path.exists():
                file_path.unlink()
                removed.append(file_path)

        return removed

    def preserve_active_files(self) -> list[str]:
        """
        Return list of files that should NOT be removed after graduation.

        Returns:
            List of filenames to preserve
        """
        return [
            "complexity-justification.md",  # Still needed for complexity gate
            "coverage.json",  # Used by test framework
            ".pre-commit-config.yaml",  # Active quality tool
            "pyproject.toml",  # Project configuration
            "requirements.txt",  # Dependencies
            "requirements-dev.txt",  # Dev dependencies
        ]

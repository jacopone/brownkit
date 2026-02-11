"""Graduation orchestrator for project transition to Speckit."""

import shutil
from datetime import datetime
from pathlib import Path

from brownfield.config import BrownfieldConfig
from brownfield.exceptions import WorkflowPhaseError
from brownfield.integration.speckit import WorkflowEnforcer
from brownfield.models.orchestrator import GraduationResult
from brownfield.models.workflow import WorkflowPhase
from brownfield.state.state_store import StateStore


class GraduationOrchestrator:
    """Orchestrates graduation to Speckit-ready state.

    Generates constitution, templates, and archives brownfield state.
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize graduation orchestrator.

        Args:
            project_root: Project root directory (uses config default if None)
        """
        self.project_root = project_root or BrownfieldConfig.get_project_root()

        # Load state
        state_path = BrownfieldConfig.get_state_path(self.project_root)
        self.state_store = StateStore(state_path)
        self.state = self.state_store.load()

        # Initialize workflow enforcer
        self.enforcer = WorkflowEnforcer(self.project_root)

        # Check if graduation phase can execute
        can_execute, error_msg = self.enforcer.can_execute_phase(WorkflowPhase.GRADUATION)
        if not can_execute:
            raise WorkflowPhaseError(
                error_msg,
                suggestion="Complete validation phase first",
            )

    def execute(self) -> GraduationResult:
        """Execute graduation workflow.

        Returns:
            GraduationResult with artifacts and metrics comparison
        """
        # Mark graduation phase as started
        self.enforcer.mark_phase_started(WorkflowPhase.GRADUATION)

        graduation_timestamp = datetime.utcnow()

        # Step 1: Generate constitution
        constitution_path = self._generate_constitution()

        # Step 2: Generate Speckit templates
        template_paths = self._generate_templates()

        # Step 3: Archive brownfield state
        archive_path = self._archive_brownfield_state()

        # Step 4: Generate graduation report
        report_path = self._generate_graduation_report(
            constitution_path, template_paths, archive_path, graduation_timestamp
        )

        # Step 5: Update state to SPEC_KIT_READY
        self.state.graduated = True
        self.state.graduation_timestamp = graduation_timestamp

        # Mark graduation as completed (transitions to SPEC_KIT_READY)
        self.enforcer.mark_phase_completed(WorkflowPhase.GRADUATION)

        self.state_store.save(self.state)

        return GraduationResult(
            constitution_path=constitution_path,
            template_paths=template_paths,
            archive_path=archive_path,
            report_path=report_path,
            graduation_timestamp=graduation_timestamp,
            baseline_metrics=self.state.baseline_metrics,
            final_metrics=self.state.current_metrics,
            success=True,
        )

    def _generate_constitution(self) -> Path:
        """Generate project constitution.md.

        Returns:
            Path to constitution file
        """
        constitution_path = self.project_root / ".specify/memory/constitution.md"
        constitution_path.parent.mkdir(parents=True, exist_ok=True)

        md = f"# {self.project_root.name} Constitution\n\n"
        md += f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += "**Status**: Graduated from Brownfield Workflow\n\n"

        md += "## Project Principles\n\n"
        md += "This project has graduated from brownfield state and now follows these principles:\n\n"

        md += "### Code Quality\n\n"
        md += f"- Test Coverage: Maintain at least {self.state.current_metrics.test_coverage:.0%}\n"
        md += f"- Complexity: Keep average complexity below {self.state.current_metrics.complexity_avg:.1f}\n"
        md += "- Documentation: All public APIs must be documented\n"
        md += "- Security: Zero critical vulnerabilities policy\n\n"

        md += "### Development Workflow\n\n"
        md += "- All features use Spec-Driven Development (Speckit)\n"
        md += "- Pre-commit hooks enforce quality gates\n"
        md += "- CI/CD pipelines validate all changes\n"
        md += "- Code review required for all PRs\n\n"

        md += "### Architecture\n\n"
        md += "- Follow standard project structure\n"
        md += "- Separation of concerns (src/, tests/, docs/)\n"
        md += "- Modular design with clear interfaces\n"
        md += "- Dependency injection for testability\n\n"

        md += "## Regression Monitoring\n\n"
        md += "Run `brownfield assess` periodically to detect quality regressions.\n"
        md += "If thresholds are breached, re-enter brownfield workflow automatically.\n\n"

        md += "## Baseline Metrics\n\n"
        md += f"- Test Coverage: {self.state.baseline_metrics.test_coverage:.1%}\n"
        md += f"- Avg Complexity: {self.state.baseline_metrics.complexity_avg:.1f}\n"
        md += f"- Max Complexity: {self.state.baseline_metrics.complexity_max}\n"
        md += f"- Critical Vulnerabilities: {self.state.baseline_metrics.critical_vulnerabilities}\n\n"

        md += "## Current Metrics\n\n"
        md += f"- Test Coverage: {self.state.current_metrics.test_coverage:.1%}\n"
        md += f"- Avg Complexity: {self.state.current_metrics.complexity_avg:.1f}\n"
        md += f"- Max Complexity: {self.state.current_metrics.complexity_max}\n"
        md += f"- Critical Vulnerabilities: {self.state.current_metrics.critical_vulnerabilities}\n\n"

        constitution_path.write_text(md, encoding="utf-8")

        return constitution_path

    def _generate_templates(self) -> dict[str, Path]:
        """Generate Speckit-compatible templates.

        Returns:
            Dictionary mapping template name to file path
        """
        templates_dir = self.project_root / ".specify/templates"
        templates_dir.mkdir(parents=True, exist_ok=True)

        template_paths = {}

        # Feature template
        feature_template = templates_dir / "feature.md"
        feature_template.write_text(
            """# Feature: {feature_name}

## Problem Statement

[Describe the problem this feature solves]

## Proposed Solution

[Describe the solution approach]

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Technical Design

[High-level technical approach]

## Implementation Plan

- [ ] Task 1
- [ ] Task 2

## Testing Strategy

- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests (if applicable)
""",
            encoding="utf-8",
        )
        template_paths["feature"] = feature_template

        # Bug template
        bug_template = templates_dir / "bug.md"
        bug_template.write_text(
            """# Bug: {bug_title}

## Description

[Describe the bug]

## Steps to Reproduce

1. Step 1
2. Step 2

## Expected Behavior

[What should happen]

## Actual Behavior

[What actually happens]

## Fix Plan

- [ ] Identify root cause
- [ ] Implement fix
- [ ] Add regression test
""",
            encoding="utf-8",
        )
        template_paths["bug"] = bug_template

        return template_paths

    def _archive_brownfield_state(self) -> Path:
        """Archive brownfield state and reports.

        Returns:
            Path to archive directory
        """
        archive_dir = self.project_root / ".specify/archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_subdir = archive_dir / f"brownfield_{timestamp_str}"
        archive_subdir.mkdir(exist_ok=True)

        # Copy state file
        state_path = BrownfieldConfig.get_state_path(self.project_root)
        if state_path.exists():
            shutil.copy(state_path, archive_subdir / "brownfield-state.json")

        # Copy reports
        reports_dir = BrownfieldConfig.get_reports_dir(self.project_root)
        if reports_dir.exists():
            shutil.copytree(
                reports_dir,
                archive_subdir / "reports",
                dirs_exist_ok=True,
            )

        # Copy memory artifacts
        memory_dir = self.project_root / ".specify/memory"
        if memory_dir.exists():
            for file in memory_dir.glob("*.md"):
                shutil.copy(file, archive_subdir / file.name)

            for file in memory_dir.glob("*.json"):
                if file.name != "constitution.md":  # Keep active constitution
                    shutil.copy(file, archive_subdir / file.name)

        return archive_subdir

    def _generate_graduation_report(
        self,
        constitution_path: Path,
        template_paths: dict[str, Path],
        archive_path: Path,
        graduation_timestamp: datetime,
    ) -> Path:
        """Generate graduation report.

        Args:
            constitution_path: Path to constitution
            template_paths: Dictionary of template paths
            archive_path: Path to archive directory
            graduation_timestamp: Timestamp of graduation

        Returns:
            Path to graduation report
        """
        report_dir = BrownfieldConfig.get_reports_dir(self.project_root)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "graduation-report.md"

        md = f"# Graduation Report: {self.project_root.name}\n\n"
        md += f"**Graduated**: {graduation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += "**Status**: ✅ Successfully transitioned to Speckit-ready state\n\n"

        md += "## Artifacts Generated\n\n"
        md += f"- **Constitution**: {constitution_path.relative_to(self.project_root)}\n"
        for name, path in template_paths.items():
            md += f"- **{name.title()} Template**: {path.relative_to(self.project_root)}\n"
        md += f"- **Archive**: {archive_path.relative_to(self.project_root)}\n\n"

        md += "## Metrics Improvement\n\n"
        md += "| Metric | Baseline | Final | Change |\n"
        md += "|--------|----------|-------|--------|\n"

        baseline = self.state.baseline_metrics
        final = self.state.current_metrics

        coverage_change = final.test_coverage - baseline.test_coverage
        md += f"| Test Coverage | {baseline.test_coverage:.1%} | {final.test_coverage:.1%} | {coverage_change:+.1%} |\n"

        complexity_change = final.complexity_avg - baseline.complexity_avg
        md += f"| Avg Complexity | {baseline.complexity_avg:.1f} | {final.complexity_avg:.1f} | {complexity_change:+.1f} |\n"

        max_complexity_change = final.complexity_max - baseline.complexity_max
        md += f"| Max Complexity | {baseline.complexity_max} | {final.complexity_max} | {max_complexity_change:+d} |\n"

        vuln_change = final.critical_vulnerabilities - baseline.critical_vulnerabilities
        md += f"| Critical Vulns | {baseline.critical_vulnerabilities} | {final.critical_vulnerabilities} | {vuln_change:+d} |\n\n"

        md += "## Next Steps\n\n"
        md += "1. **Use Speckit for new features**: `specify` command for spec-driven development\n"
        md += "2. **Monitor quality**: Run `brownfield assess` monthly to detect regressions\n"
        md += "3. **Review constitution**: Ensure team understands project principles\n"
        md += "4. **Leverage templates**: Use generated templates for consistent feature development\n"
        md += "5. **Maintain standards**: Pre-commit hooks enforce quality automatically\n\n"

        md += "## Graduation Complete! 🎓\n\n"
        md += f"Project **{self.project_root.name}** is now Speckit-ready and follows spec-driven development.\n"

        report_path.write_text(md, encoding="utf-8")

        return report_path

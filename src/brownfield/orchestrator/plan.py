"""Plan generation orchestrator for unified remediation roadmap."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from brownfield.assessment.language_detector import LanguageDetector
from brownfield.config import BrownfieldConfig
from brownfield.models.orchestrator import QualityPlan, StructurePlan, TestingPlan, UnifiedPlan
from brownfield.orchestrator.utils.plan_loader import save_unified_plan
from brownfield.plugins.registry import get_handler
from brownfield.remediation.quality import QualityGatesInstaller
from brownfield.remediation.structure import StructurePlanGenerator
from brownfield.remediation.testing import TestingBootstrapper
from brownfield.state.state_store import StateStore


class PlanOrchestrator:
    """Orchestrates unified remediation plan generation.

    Coordinates structure, testing, and quality analysis to generate
    a comprehensive remediation roadmap with effort estimates and dependencies.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize plan orchestrator.

        Args:
            project_root: Project root directory (uses config default if None)
        """
        self.project_root = project_root or BrownfieldConfig.get_project_root()

        # Ensure state exists
        state_path = BrownfieldConfig.get_state_path(self.project_root)
        if not state_path.exists():
            raise FileNotFoundError(
                "Brownfield state not found. Run 'brownfield assess' first."
            )

        # Load state
        self.state_store = StateStore(state_path)
        self.state = self.state_store.load()

        # Detect language
        detector = LanguageDetector()
        self.lang_detection = detector.detect(self.project_root)
        self.handler = get_handler(self.lang_detection.language)

    def execute(self) -> UnifiedPlan:
        """Generate unified remediation plan.

        Returns:
            UnifiedPlan with structure, testing, quality plans and estimates
        """
        # Step 1: Analyze structure needs
        structure_plan = self._analyze_structure()

        # Step 2: Analyze testing needs
        testing_plan = self._analyze_testing()

        # Step 3: Analyze quality needs
        quality_plan = self._analyze_quality()

        # Step 4: Calculate estimates and dependencies
        estimated_duration_hours = self._estimate_duration(
            structure_plan, testing_plan, quality_plan
        )

        dependencies = self._determine_dependencies(structure_plan)

        total_tasks = self._count_tasks(structure_plan, testing_plan, quality_plan)

        # Step 5: Generate markdown plan
        plan_markdown = self._generate_markdown(
            structure_plan,
            testing_plan,
            quality_plan,
            estimated_duration_hours,
            dependencies,
        )

        # Step 6: Save plan
        plan_path = self.project_root / ".specify/memory/plan.md"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(plan_markdown, encoding="utf-8")

        # Create unified plan object
        unified_plan = UnifiedPlan(
            structure_plan=structure_plan,
            testing_plan=testing_plan,
            quality_plan=quality_plan,
            estimated_duration_hours=estimated_duration_hours,
            dependencies=dependencies,
            plan_markdown=plan_markdown,
            plan_path=plan_path,
            total_tasks=total_tasks,
        )

        # Save to JSON for state persistence
        save_unified_plan(unified_plan, self.project_root)

        return unified_plan

    def _analyze_structure(self) -> Optional[StructurePlan]:
        """Analyze structure needs using StructurePlanGenerator.

        Returns:
            StructurePlan or None if already compliant
        """
        generator = StructurePlanGenerator(self.project_root, self.lang_detection)
        analysis = generator.analyze_structure()

        if analysis.compliant:
            return None

        # Convert analysis to StructurePlan
        files_to_move = {
            str(op.source): str(op.destination) for op in analysis.files_to_move
        }

        directories_to_create = [str(d) for d in analysis.missing_directories]

        issues_found = [
            f"{len(analysis.files_to_move)} files need to be moved",
            f"{len(analysis.missing_directories)} directories need to be created",
        ]

        return StructurePlan(
            files_to_move=files_to_move,
            directories_to_create=directories_to_create,
            compliant=analysis.compliant,
            issues_found=issues_found,
        )

    def _analyze_testing(self) -> TestingPlan:
        """Analyze testing needs.

        Returns:
            TestingPlan with framework and test counts
        """
        bootstrapper = TestingBootstrapper(self.handler, self.project_root)

        # Identify core modules
        core_modules = bootstrapper._identify_core_modules()

        # Estimate test needs (heuristic: 1 smoke test per module, contracts for top 30%)
        smoke_tests_needed = min(len(core_modules), 10)  # Cap at 10 smoke tests
        contract_tests_needed = max(int(len(core_modules) * 0.3), 3)  # 30% or min 3

        # Get current coverage from state
        current_coverage = self.state.current_metrics.test_coverage
        target_coverage = 0.6  # 60% target

        # Determine framework from handler
        framework = self._determine_test_framework()

        return TestingPlan(
            core_modules=core_modules[:10],  # Limit to top 10 for display
            smoke_tests_needed=smoke_tests_needed,
            contract_tests_needed=contract_tests_needed,
            current_coverage=current_coverage,
            target_coverage=target_coverage,
            framework=framework,
        )

    def _analyze_quality(self) -> QualityPlan:
        """Analyze quality gate needs.

        Returns:
            QualityPlan with linter, formatter, hooks
        """
        # Determine linter and formatter based on language
        linter, formatter = self._determine_quality_tools()

        # Count complexity violations from current metrics
        complexity_violations = len(
            self.state.current_metrics.complexity_violations or []
        )

        # Count security issues
        security_issues = (
            self.state.current_metrics.critical_vulnerabilities
            + self.state.current_metrics.high_vulnerabilities
        )

        # Determine hooks to install
        hooks_to_install = ["pre-commit", "pre-push"]

        return QualityPlan(
            linter=linter,
            formatter=formatter,
            hooks_to_install=hooks_to_install,
            complexity_violations=complexity_violations,
            security_issues=security_issues,
        )

    def _determine_test_framework(self) -> str:
        """Determine appropriate test framework for language."""
        framework_map = {
            "python": "pytest",
            "javascript": "jest",
            "rust": "cargo test",
            "go": "go test",
        }
        return framework_map.get(self.lang_detection.language, "unknown")

    def _determine_quality_tools(self) -> tuple[str, str]:
        """Determine linter and formatter for language."""
        tools_map = {
            "python": ("ruff", "ruff format"),
            "javascript": ("eslint", "prettier"),
            "rust": ("clippy", "rustfmt"),
            "go": ("golangci-lint", "gofmt"),
        }
        return tools_map.get(self.lang_detection.language, ("unknown", "unknown"))

    def _estimate_duration(
        self,
        structure_plan: Optional[StructurePlan],
        testing_plan: TestingPlan,
        quality_plan: QualityPlan,
    ) -> float:
        """Estimate total remediation duration in hours."""
        duration = 0.0

        # Structure: 0.5 hours per file + 0.25 hours per directory
        if structure_plan and not structure_plan.compliant:
            duration += len(structure_plan.files_to_move) * 0.5
            duration += len(structure_plan.directories_to_create) * 0.25

        # Testing: 1 hour per smoke test + 2 hours per contract test
        duration += testing_plan.smoke_tests_needed * 1.0
        duration += testing_plan.contract_tests_needed * 2.0

        # Quality: 2 hours setup + 0.1 hours per violation + 0.5 hours per security issue
        duration += 2.0  # Setup time
        duration += quality_plan.complexity_violations * 0.1
        duration += quality_plan.security_issues * 0.5

        return round(duration, 1)

    def _determine_dependencies(
        self, structure_plan: Optional[StructurePlan]
    ) -> dict[str, list[str]]:
        """Determine phase dependencies."""
        dependencies = {
            "structure": [],
            "testing": ["structure"] if structure_plan else [],
            "quality": ["testing"],
            "validation": ["quality"],
            "graduation": ["validation"],
        }
        return dependencies

    def _count_tasks(
        self,
        structure_plan: Optional[StructurePlan],
        testing_plan: TestingPlan,
        quality_plan: QualityPlan,
    ) -> int:
        """Count total tasks across all phases."""
        count = 0

        if structure_plan:
            count += len(structure_plan.files_to_move)
            count += len(structure_plan.directories_to_create)

        count += testing_plan.smoke_tests_needed
        count += testing_plan.contract_tests_needed

        count += len(quality_plan.hooks_to_install)
        count += 2  # Linter + formatter setup

        return count

    def _generate_markdown(
        self,
        structure_plan: Optional[StructurePlan],
        testing_plan: TestingPlan,
        quality_plan: QualityPlan,
        estimated_duration_hours: float,
        dependencies: dict[str, list[str]],
    ) -> str:
        """Generate comprehensive markdown plan."""
        md = f"# Brownfield Remediation Plan\n\n"
        md += f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Project**: {self.project_root.name}\n"
        md += f"**Language**: {self.lang_detection.language}\n"
        md += f"**Estimated Duration**: {estimated_duration_hours:.1f} hours\n\n"

        md += "## Overview\n\n"
        md += "This plan outlines the steps needed to transform this brownfield project into a Speckit-ready state.\n\n"

        # Structure phase
        if structure_plan and not structure_plan.compliant:
            md += "## Phase 1: Structure\n\n"
            md += f"**Status**: {len(structure_plan.issues_found)} issues found\n\n"
            md += "### Directories to Create\n\n"
            for dir_path in structure_plan.directories_to_create:
                md += f"- `{dir_path}`\n"
            md += "\n### Files to Move\n\n"
            for src, dest in list(structure_plan.files_to_move.items())[:10]:
                md += f"- `{src}` → `{dest}`\n"
            md += "\n"
        else:
            md += "## Phase 1: Structure\n\n"
            md += "**Status**: ✅ Already compliant\n\n"

        # Testing phase
        md += "## Phase 2: Testing\n\n"
        md += f"**Framework**: {testing_plan.framework}\n"
        md += f"**Current Coverage**: {testing_plan.current_coverage:.1%}\n"
        md += f"**Target Coverage**: {testing_plan.target_coverage:.1%}\n\n"
        md += "### Tasks\n\n"
        md += f"1. Generate {testing_plan.smoke_tests_needed} smoke tests for core modules\n"
        md += f"2. Generate {testing_plan.contract_tests_needed} contract tests\n"
        md += f"3. Configure {testing_plan.framework} test framework\n"
        md += f"4. Achieve {testing_plan.target_coverage:.0%} test coverage\n\n"

        # Quality phase
        md += "## Phase 3: Quality\n\n"
        md += f"**Linter**: {quality_plan.linter}\n"
        md += f"**Formatter**: {quality_plan.formatter}\n"
        md += f"**Complexity Violations**: {quality_plan.complexity_violations}\n"
        md += f"**Security Issues**: {quality_plan.security_issues}\n\n"
        md += "### Tasks\n\n"
        md += f"1. Install and configure {quality_plan.linter}\n"
        md += f"2. Install and configure {quality_plan.formatter}\n"
        md += f"3. Set up pre-commit hooks: {', '.join(quality_plan.hooks_to_install)}\n"
        if quality_plan.complexity_violations > 0:
            md += f"4. Resolve {quality_plan.complexity_violations} complexity violations\n"
        if quality_plan.security_issues > 0:
            md += f"5. Address {quality_plan.security_issues} security issues\n"
        md += "\n"

        # Dependencies
        md += "## Phase Dependencies\n\n"
        for phase, prereqs in dependencies.items():
            prereqs_str = ", ".join(prereqs) if prereqs else "None"
            md += f"- **{phase}**: Requires {prereqs_str}\n"

        md += "\n## Next Steps\n\n"
        md += "1. Review this plan\n"
        md += "2. Run `brownfield structure` to begin structure remediation\n"
        md += "3. Follow the workflow: structure → testing → quality → validation → graduation\n"

        return md

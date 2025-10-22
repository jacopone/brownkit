"""Result models for workflow orchestrators."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from brownfield.models.assessment import LanguageDetection, Metrics, TechDebtCategory
from brownfield.models.checkpoint import Task
from brownfield.models.gate import ReadinessGate
from brownfield.models.state import Phase, ReEntryEvent


@dataclass
class AssessmentResult:
    """Result from AssessmentOrchestrator execution.

    Contains comprehensive assessment data including language detection,
    baseline metrics, tech debt analysis, and optional regression detection.
    """

    language_detection: LanguageDetection
    baseline_metrics: Metrics
    tech_debt: list[TechDebtCategory]
    regression: Optional[ReEntryEvent]
    report_path: Path
    duration_seconds: int
    current_phase: Phase


@dataclass
class StructurePlan:
    """Structure remediation plan details."""

    files_to_move: dict[str, str]  # source -> destination
    directories_to_create: list[str]
    compliant: bool
    issues_found: list[str]


@dataclass
class TestingPlan:
    """Testing infrastructure plan details."""

    core_modules: list[Path]
    smoke_tests_needed: int
    contract_tests_needed: int
    current_coverage: float
    target_coverage: float
    framework: str


@dataclass
class QualityPlan:
    """Quality gates installation plan details."""

    linter: str
    formatter: str
    hooks_to_install: list[str]
    complexity_violations: int
    security_issues: int


@dataclass
class UnifiedPlan:
    """Unified remediation plan combining all phases.

    Combines structure, testing, and quality plans into a single
    comprehensive remediation roadmap with effort estimates.
    """

    structure_plan: Optional[StructurePlan]
    testing_plan: TestingPlan
    quality_plan: QualityPlan
    estimated_duration_hours: float
    dependencies: dict[str, list[str]]  # phase -> prerequisite phases
    plan_markdown: str
    plan_path: Path
    total_tasks: int


@dataclass
class RemediationResult:
    """Result from RemediationOrchestrator execution.

    Tracks tasks completed, failures, git commits, and metrics improvements.
    """

    phase: Phase
    tasks_completed: list[Task]
    tasks_failed: list[Task]
    git_commits: list[str]
    checkpoint_path: Optional[Path]
    metrics_after: Metrics
    success: bool
    duration_seconds: int


@dataclass
class GateResult:
    """Individual gate validation result."""

    gate: ReadinessGate
    passed: bool
    current_value: float
    threshold: float
    message: str


@dataclass
class ValidationResult:
    """Result from ValidationOrchestrator execution.

    Contains all gate validation results and recommended next steps.
    """

    all_passed: bool
    gates: list[GateResult]
    failed_count: int
    report_path: Path
    recommended_phase: Optional[Phase]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GraduationResult:
    """Result from GraduationOrchestrator execution.

    Contains paths to generated artifacts and graduation metadata.
    """

    constitution_path: Path
    template_paths: dict[str, Path]
    archive_path: Path
    report_path: Path
    graduation_timestamp: datetime
    baseline_metrics: Metrics
    final_metrics: Metrics
    success: bool

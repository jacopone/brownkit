"""Validation orchestrator for readiness gate checking."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from brownfield.assessment.metrics_collector import MetricsCollector
from brownfield.config import BrownfieldConfig
from brownfield.exceptions import WorkflowPhaseError
from brownfield.integration.speckit import WorkflowEnforcer
from brownfield.models.gate import ReadinessGate
from brownfield.models.orchestrator import GateResult, ValidationResult
from brownfield.models.state import Phase
from brownfield.models.workflow import WorkflowPhase
from brownfield.state.state_store import StateStore


@dataclass
class GateDefinition:
    """Simple gate definition template."""

    name: str
    threshold: float
    description: str


class ValidationOrchestrator:
    """Orchestrates readiness gate validation for graduation.

    Validates that all quality thresholds are met before allowing graduation.
    """

    # Gate definition templates (not full ReadinessGate objects)
    GATE_DEFINITIONS = [
        GateDefinition(
            name="test_coverage",
            threshold=0.6,
            description="Test coverage must be at least 60%",
        ),
        GateDefinition(
            name="complexity_avg",
            threshold=10.0,
            description="Average complexity must be below 10",
        ),
        GateDefinition(
            name="complexity_max",
            threshold=15.0,
            description="Maximum complexity must be below 15",
        ),
        GateDefinition(
            name="critical_vulnerabilities",
            threshold=0.0,
            description="No critical vulnerabilities allowed",
        ),
        GateDefinition(
            name="high_vulnerabilities",
            threshold=2.0,
            description="Maximum 2 high vulnerabilities allowed",
        ),
        GateDefinition(
            name="documentation_coverage",
            threshold=0.5,
            description="Documentation coverage must be at least 50%",
        ),
        GateDefinition(
            name="build_status",
            threshold=1.0,  # 1 = passing
            description="Build must be passing",
        ),
    ]

    def __init__(self, project_root: Path | None = None):
        """Initialize validation orchestrator.

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

        # Check if validation phase can execute
        can_execute, error_msg = self.enforcer.can_execute_phase(WorkflowPhase.VALIDATION)
        if not can_execute:
            raise WorkflowPhaseError(
                error_msg,
                suggestion="Complete prerequisite phases first",
            )

    def execute(self) -> ValidationResult:
        """Execute validation against all readiness gates.

        Returns:
            ValidationResult with gate status and recommendations
        """
        # Mark validation phase as started
        self.enforcer.mark_phase_started(WorkflowPhase.VALIDATION)

        # Collect current metrics (fresh validation)
        from brownfield.assessment.language_detector import LanguageDetector

        detector = LanguageDetector()
        lang_detection = detector.detect(self.project_root)

        collector = MetricsCollector()
        current_metrics = collector.collect(self.project_root, lang_detection.language, mode="quick")

        # Validate each gate
        gate_results: list[GateResult] = []

        for gate_def in self.GATE_DEFINITIONS:
            gate_result = self._validate_gate(gate_def, current_metrics)
            gate_results.append(gate_result)

        # Calculate summary
        failed_count = sum(1 for gr in gate_results if not gr.passed)
        all_passed = failed_count == 0

        # Determine recommended phase if validation failed
        recommended_phase = None
        if not all_passed:
            recommended_phase = self._determine_recommended_phase(gate_results)

        # Generate report
        report_path = self._generate_report(gate_results, all_passed)

        # Update state
        self.state.current_metrics = current_metrics

        # Mark validation as completed
        self.enforcer.mark_phase_completed(WorkflowPhase.VALIDATION)

        # Note: Graduation happens in GraduationOrchestrator, not here
        # Validation just confirms readiness for graduation

        self.state_store.save(self.state)

        return ValidationResult(
            all_passed=all_passed,
            gates=gate_results,
            failed_count=failed_count,
            report_path=report_path,
            recommended_phase=recommended_phase,
            timestamp=datetime.utcnow(),
        )

    def _validate_gate(self, gate_def: GateDefinition, metrics) -> GateResult:
        """Validate a single readiness gate.

        Args:
            gate_def: GateDefinition template to validate
            metrics: Current metrics

        Returns:
            GateResult with pass/fail status
        """
        # Get current value based on gate name
        if gate_def.name == "test_coverage":
            current_value = metrics.test_coverage
            passed = current_value >= gate_def.threshold
            message = f"{'✓' if passed else '✗'} Coverage: {current_value:.1%}"
            verification_cmd = "pytest --cov"
            remediation = "Add more tests to increase coverage"

        elif gate_def.name == "complexity_avg":
            current_value = metrics.complexity_avg
            passed = current_value <= gate_def.threshold
            message = f"{'✓' if passed else '✗'} Avg complexity: {current_value:.1f}"
            verification_cmd = "lizard --CCN 10"
            remediation = "Refactor complex functions"

        elif gate_def.name == "complexity_max":
            current_value = metrics.complexity_max
            passed = current_value <= gate_def.threshold
            message = f"{'✓' if passed else '✗'} Max complexity: {current_value}"
            verification_cmd = "lizard --CCN 15"
            remediation = "Break down most complex functions"

        elif gate_def.name == "critical_vulnerabilities":
            current_value = metrics.critical_vulnerabilities
            passed = current_value <= gate_def.threshold
            message = f"{'✓' if passed else '✗'} Critical vulns: {current_value}"
            verification_cmd = "bandit -r src"
            remediation = "Fix all critical security vulnerabilities"

        elif gate_def.name == "high_vulnerabilities":
            current_value = metrics.high_vulnerabilities
            passed = current_value <= gate_def.threshold
            message = f"{'✓' if passed else '✗'} High vulns: {current_value}"
            verification_cmd = "bandit -r src"
            remediation = "Address high-priority security issues"

        elif gate_def.name == "documentation_coverage":
            current_value = metrics.documentation_coverage
            passed = current_value >= gate_def.threshold
            message = f"{'✓' if passed else '✗'} Doc coverage: {current_value:.1%}"
            verification_cmd = "pydoc-markdown"
            remediation = "Add docstrings to public APIs"

        elif gate_def.name == "build_status":
            # Convert build status to numeric (1=passing, 0=failing/unknown)
            current_value = 1.0 if metrics.build_status == "passing" else 0.0
            passed = current_value >= gate_def.threshold
            message = f"{'✓' if passed else '✗'} Build: {metrics.build_status}"
            verification_cmd = "python setup.py build"
            remediation = "Fix build errors"

        else:
            current_value = 0.0
            passed = False
            message = f"✗ Unknown gate: {gate_def.name}"
            verification_cmd = ""
            remediation = "Unknown gate type"

        # Create full ReadinessGate object
        gate = ReadinessGate(
            name=gate_def.name,
            description=gate_def.description,
            threshold=gate_def.threshold,
            current_value=current_value,
            passed=passed,
            verification_command=verification_cmd,
            remediation_guidance=remediation,
        )

        return GateResult(
            gate=gate,
            passed=passed,
            current_value=current_value,
            threshold=gate_def.threshold,
            message=message,
        )

    def _determine_recommended_phase(self, gate_results: list[GateResult]) -> Phase | None:
        """Determine which phase to return to based on failed gates.

        Args:
            gate_results: List of gate results

        Returns:
            Recommended phase to address failures
        """
        failed_gates = [gr for gr in gate_results if not gr.passed]

        # Prioritize by severity
        for gate_result in failed_gates:
            gate_name = gate_result.gate.name

            if gate_name in ["test_coverage"]:
                return Phase.TESTING

            if gate_name in ["complexity_avg", "complexity_max", "documentation_coverage"]:
                return Phase.QUALITY

            if gate_name in ["critical_vulnerabilities", "high_vulnerabilities", "build_status"]:
                return Phase.QUALITY

        return Phase.QUALITY  # Default recommendation

    def _generate_report(self, gate_results: list[GateResult], all_passed: bool) -> Path:
        """Generate validation report markdown.

        Args:
            gate_results: List of gate results
            all_passed: Whether all gates passed

        Returns:
            Path to generated report
        """
        report_dir = self.project_root / ".specify/memory"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "validation-report.md"

        md = "# Validation Report\n\n"
        md += f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Status**: {'✅ PASSED' if all_passed else '❌ FAILED'}\n\n"

        md += "## Readiness Gates\n\n"

        for gate_result in gate_results:
            status = "✅" if gate_result.passed else "❌"
            md += f"### {status} {gate_result.gate.name}\n\n"
            md += f"- **Description**: {gate_result.gate.description}\n"
            md += f"- **Current Value**: {gate_result.current_value:.2f}\n"
            md += f"- **Threshold**: {gate_result.threshold:.2f}\n"
            md += f"- **Status**: {gate_result.message}\n\n"

        if not all_passed:
            failed_count = sum(1 for gr in gate_results if not gr.passed)
            md += "\n## Action Required\n\n"
            md += f"**{failed_count} gate(s) failed validation.**\n\n"
            md += "Please address the failed gates before attempting graduation.\n"

        report_path.write_text(md, encoding="utf-8")

        return report_path

"""Assessment workflow orchestrator."""

import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from brownfield.assessment.language_detector import LanguageDetector
from brownfield.assessment.metrics_collector import MetricsCollector
from brownfield.assessment.report_generator import ReportGenerator
from brownfield.assessment.tech_debt_analyzer import TechDebtAnalyzer
from brownfield.config import BrownfieldConfig
from brownfield.exceptions import (
    LanguageDetectionError,
    MetricsCollectionError,
    StateNotFoundError,
)
from brownfield.models.orchestrator import AssessmentResult
from brownfield.models.state import BrownfieldState, Phase
from brownfield.orchestrator.phase_machine import PhaseOrchestrator
from brownfield.state.report_writer import ReportWriter
from brownfield.state.state_store import StateStore


class AssessmentOrchestrator:
    """Orchestrates comprehensive codebase assessment workflow.

    Coordinates language detection, metrics collection, tech debt analysis,
    and state management (initialization or regression detection).
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        language_override: Optional[str] = None,
        quick_mode: bool = True,
    ):
        """Initialize assessment orchestrator.

        Args:
            project_root: Project root directory (uses config default if None)
            language_override: Override automatic language detection
            quick_mode: Use quick sampling analysis vs full comprehensive
        """
        self.project_root = project_root or BrownfieldConfig.get_project_root()
        self.language_override = language_override or BrownfieldConfig.get_forced_language()
        self.quick_mode = quick_mode

        # Ensure directories exist
        BrownfieldConfig.ensure_directories(self.project_root)

        # Initialize state store
        state_path = BrownfieldConfig.get_state_path(self.project_root)
        self.state_store = StateStore(state_path)

        # Initialize analysis components
        self.language_detector = LanguageDetector()
        self.metrics_collector = MetricsCollector()
        self.tech_debt_analyzer = TechDebtAnalyzer()
        self.report_generator = ReportGenerator()

    def execute(self, output_path: Optional[Path] = None) -> AssessmentResult:
        """Execute assessment workflow.

        Args:
            output_path: Path for assessment report (default: .specify/memory/assessment-report.md)

        Returns:
            AssessmentResult with language, metrics, tech debt, and optional regression

        Raises:
            LanguageDetectionError: If language detection fails
            MetricsCollectionError: If metrics collection fails
        """
        start_time = time.time()

        # Default output path
        if output_path is None:
            output_path = self.project_root / ".specify/memory/assessment-report.md"

        # Step 1: Language detection
        try:
            lang_detection = self.language_detector.detect(self.project_root)
        except Exception as e:
            raise LanguageDetectionError(str(e)) from e

        # Step 2: Metrics collection
        mode = "quick" if self.quick_mode else "full"
        detected_language = self.language_override or lang_detection.language

        try:
            metrics = self.metrics_collector.collect(
                self.project_root,
                detected_language,
                mode
            )
        except Exception as e:
            raise MetricsCollectionError(str(e)) from e

        # Step 3: Tech debt analysis
        tech_debt = self.tech_debt_analyzer.analyze(self.project_root)

        # Step 4: Generate report
        duration = int(time.time() - start_time)
        report = self.report_generator.generate(
            project_name=self.project_root.name,
            project_root=self.project_root,
            language_detection=lang_detection,
            baseline_metrics=metrics,
            tech_debt=tech_debt,
            analysis_mode=mode,
            duration_seconds=duration,
        )

        # Step 5: Write report
        ReportWriter.write_assessment_report(report, output_path)

        # Step 6: State management (initialization or regression detection)
        regression = None
        current_phase = Phase.STRUCTURE

        if self.state_store.exists():
            # Load existing state and check for regression
            existing_state = self.state_store.load()

            # Update current metrics
            existing_state.current_metrics = metrics

            # Detect regression if graduated
            regression = self.state_store.detect_regression(existing_state)

            if regression:
                # Handle re-entry via phase orchestrator
                phase_orchestrator = PhaseOrchestrator(existing_state)
                current_phase = phase_orchestrator.handle_re_entry(regression)
            else:
                current_phase = existing_state.current_phase

            # Save updated state
            self.state_store.save(existing_state)

        else:
            # Initialize new state (first assessment)
            state = BrownfieldState(
                schema_version="1.0",
                project_root=self.project_root,
                current_phase=Phase.STRUCTURE,
                baseline_metrics=metrics,
                current_metrics=metrics,
                phase_timestamps={"assessment": datetime.utcnow()},
            )
            self.state_store.save(state)

        # Return assessment result
        return AssessmentResult(
            language_detection=lang_detection,
            baseline_metrics=metrics,
            tech_debt=tech_debt,
            regression=regression,
            report_path=output_path,
            duration_seconds=duration,
            current_phase=current_phase,
        )

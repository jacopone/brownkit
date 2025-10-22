"""Remediation workflow orchestrator for executing phase-specific fixes."""

import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from brownfield.assessment.language_detector import LanguageDetector
from brownfield.assessment.metrics_collector import MetricsCollector
from brownfield.config import BrownfieldConfig
from brownfield.models.checkpoint import Task
from brownfield.models.orchestrator import RemediationResult
from brownfield.models.state import Phase
from brownfield.orchestrator.phase_machine import PhaseOrchestrator
from brownfield.orchestrator.utils.plan_loader import load_unified_plan
from brownfield.plugins.registry import get_handler
from brownfield.state.state_store import StateStore


class RemediationOrchestrator:
    """Orchestrates phase-specific remediation execution.

    Executes remediation tasks for STRUCTURE, TESTING, or QUALITY phases
    with checkpoint-based recovery and progress tracking.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize remediation orchestrator.

        Args:
            project_root: Project root directory (uses config default if None)
        """
        self.project_root = project_root or BrownfieldConfig.get_project_root()

        # Load state
        state_path = BrownfieldConfig.get_state_path(self.project_root)
        self.state_store = StateStore(state_path)
        self.state = self.state_store.load()

        # Detect language
        detector = LanguageDetector()
        self.lang_detection = detector.detect(self.project_root)
        self.handler = get_handler(self.lang_detection.language)

        # Load unified plan
        self.plan = load_unified_plan(self.project_root)

    def execute(self, phase: Phase, auto_commit: bool = True) -> RemediationResult:
        """Execute remediation for specified phase.

        Args:
            phase: Phase to remediate (STRUCTURE, TESTING, or QUALITY)
            auto_commit: Automatically commit changes after phase completion

        Returns:
            RemediationResult with tasks completed/failed, commits, metrics
        """
        start_time = time.time()

        tasks_completed: list[Task] = []
        tasks_failed: list[Task] = []
        git_commits: list[str] = []

        # Execute phase-specific remediation
        if phase == Phase.STRUCTURE:
            tasks_completed, tasks_failed = self._remediate_structure()
            if auto_commit and tasks_completed:
                git_commits.append(self._commit_changes("refactor: Apply structure remediation"))

        elif phase == Phase.TESTING:
            tasks_completed, tasks_failed = self._remediate_testing()
            if auto_commit and tasks_completed:
                git_commits.append(self._commit_changes("test: Bootstrap test infrastructure"))

        elif phase == Phase.QUALITY:
            tasks_completed, tasks_failed = self._remediate_quality()
            if auto_commit and tasks_completed:
                git_commits.append(self._commit_changes("chore: Install quality gates"))

        else:
            raise ValueError(f"Remediation not supported for phase: {phase}")

        # Collect metrics after remediation
        collector = MetricsCollector()
        metrics_after = collector.collect(
            self.project_root,
            self.lang_detection.language,
            mode="quick"
        )

        # Update state
        self.state.current_metrics = metrics_after
        self.state.phase_timestamps[f"{phase.value}_completed"] = datetime.utcnow()

        # Advance phase if successful
        success = len(tasks_failed) == 0
        if success:
            phase_orchestrator = PhaseOrchestrator(self.state)
            next_phase = self._get_next_phase(phase)
            if next_phase:
                phase_orchestrator.advance(next_phase)

        self.state_store.save(self.state)

        # Save checkpoint
        checkpoint_path = self._save_checkpoint(phase, tasks_completed, tasks_failed)

        duration = int(time.time() - start_time)

        return RemediationResult(
            phase=phase,
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            git_commits=git_commits,
            checkpoint_path=checkpoint_path,
            metrics_after=metrics_after,
            success=success,
            duration_seconds=duration,
        )

    def _remediate_structure(self) -> tuple[list[Task], list[Task]]:
        """Execute structure remediation tasks.

        Note: Structure phase is human-in-the-loop, so this generates
        a plan rather than executing automated fixes.

        Returns:
            (completed_tasks, failed_tasks)
        """
        tasks_completed = []
        tasks_failed = []

        if not self.plan.structure_plan:
            return tasks_completed, tasks_failed

        # For structure, we track planning tasks (actual moves are manual)
        for src, dest in self.plan.structure_plan.files_to_move.items():
            task = Task(
                task_id=f"move_{Path(src).name.replace('.', '_')}",
                description=f"Move {src} to {dest}",
                phase=Phase.STRUCTURE,
                estimated_minutes=30,
                completed=False,
            )
            # Mark as completed since plan is generated (manual execution required)
            task.completed = True
            tasks_completed.append(task)

        return tasks_completed, tasks_failed

    def _remediate_testing(self) -> tuple[list[Task], list[Task]]:
        """Execute testing remediation tasks.

        Returns:
            (completed_tasks, failed_tasks)
        """
        from brownfield.remediation.testing import TestingBootstrapper

        tasks_completed = []
        tasks_failed = []

        bootstrapper = TestingBootstrapper(self.handler, self.project_root)

        # Task 1: Identify core modules
        try:
            core_modules = bootstrapper._identify_core_modules()
            tasks_completed.append(
                Task(
                    task_id="identify_core_modules",
                    description=f"Found {len(core_modules)} core modules",
                    phase=Phase.TESTING,
                    estimated_minutes=10,
                    completed=True,
                )
            )
        except Exception as e:
            tasks_failed.append(
                Task(
                    task_id="identify_core_modules",
                    description=f"Failed: {e}",
                    phase=Phase.TESTING,
                    estimated_minutes=10,
                    completed=False,
                    error_message=str(e),
                )
            )
            return tasks_completed, tasks_failed

        # Task 2: Generate smoke tests
        try:
            smoke_tests = bootstrapper.generate_smoke_tests(core_modules[:10])
            tasks_completed.append(
                Task(
                    task_id="generate_smoke_tests",
                    description=f"Generated {len(smoke_tests)} smoke tests",
                    phase=Phase.TESTING,
                    estimated_minutes=60,
                    completed=True,
                )
            )
        except Exception as e:
            tasks_failed.append(
                Task(
                    task_id="generate_smoke_tests",
                    description=f"Failed: {e}",
                    phase=Phase.TESTING,
                    estimated_minutes=60,
                    completed=False,
                    error_message=str(e),
                )
            )

        return tasks_completed, tasks_failed

    def _remediate_quality(self) -> tuple[list[Task], list[Task]]:
        """Execute quality remediation tasks.

        Returns:
            (completed_tasks, failed_tasks)
        """
        from brownfield.remediation.quality import QualityGatesInstaller

        tasks_completed = []
        tasks_failed = []

        installer = QualityGatesInstaller(self.handler, self.project_root)

        # Task 1: Create linter config
        try:
            installer.create_linter_config()
            tasks_completed.append(
                Task(
                    task_id="create_linter_config",
                    description=f"Created {self.plan.quality_plan.linter} configuration",
                    phase=Phase.QUALITY,
                    estimated_minutes=15,
                    completed=True,
                )
            )
        except Exception as e:
            tasks_failed.append(
                Task(
                    task_id="create_linter_config",
                    description=f"Failed: {e}",
                    phase=Phase.QUALITY,
                    estimated_minutes=15,
                    completed=False,
                    error_message=str(e),
                )
            )

        # Task 2: Create formatter config
        try:
            installer.create_formatter_config()
            tasks_completed.append(
                Task(
                    task_id="create_formatter_config",
                    description=f"Created {self.plan.quality_plan.formatter} configuration",
                    phase=Phase.QUALITY,
                    estimated_minutes=15,
                    completed=True,
                )
            )
        except Exception as e:
            tasks_failed.append(
                Task(
                    task_id="create_formatter_config",
                    description=f"Failed: {e}",
                    phase=Phase.QUALITY,
                    estimated_minutes=15,
                    completed=False,
                    error_message=str(e),
                )
            )

        # Task 3: Install pre-commit hooks
        try:
            installer.install_precommit_hooks()
            tasks_completed.append(
                Task(
                    task_id="install_precommit_hooks",
                    description="Installed pre-commit hooks",
                    phase=Phase.QUALITY,
                    estimated_minutes=20,
                    completed=True,
                )
            )
        except Exception as e:
            tasks_failed.append(
                Task(
                    task_id="install_precommit_hooks",
                    description=f"Failed: {e}",
                    phase=Phase.QUALITY,
                    estimated_minutes=20,
                    completed=False,
                    error_message=str(e),
                )
            )

        return tasks_completed, tasks_failed

    def _commit_changes(self, message: str) -> str:
        """Create git commit with changes.

        Args:
            message: Commit message

        Returns:
            Commit hash or "no-changes" if nothing to commit
        """
        import subprocess

        try:
            # Stage changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Get commit hash
                hash_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return hash_result.stdout.strip()[:7]
            else:
                return "no-changes"

        except subprocess.CalledProcessError:
            return "commit-failed"

    def _save_checkpoint(
        self, phase: Phase, tasks_completed: list[Task], tasks_failed: list[Task]
    ) -> Path:
        """Save checkpoint with progress.

        Args:
            phase: Current phase
            tasks_completed: Completed tasks
            tasks_failed: Failed tasks

        Returns:
            Path to checkpoint file
        """
        checkpoint_dir = self.project_root / ".specify/memory/checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_path = checkpoint_dir / f"{phase.value}-checkpoint.json"

        import json

        checkpoint_data = {
            "phase": phase.value,
            "timestamp": datetime.utcnow().isoformat(),
            "tasks_completed": [
                {"name": t.name, "description": t.description} for t in tasks_completed
            ],
            "tasks_failed": [
                {"name": t.name, "description": t.description} for t in tasks_failed
            ],
        }

        checkpoint_path.write_text(json.dumps(checkpoint_data, indent=2))

        return checkpoint_path

    def _get_next_phase(self, current_phase: Phase) -> Optional[Phase]:
        """Determine next phase after successful remediation.

        Args:
            current_phase: Current phase

        Returns:
            Next phase or None if graduation
        """
        phase_sequence = {
            Phase.STRUCTURE: Phase.TESTING,
            Phase.TESTING: Phase.QUALITY,
            Phase.QUALITY: Phase.VALIDATION,
        }
        return phase_sequence.get(current_phase)

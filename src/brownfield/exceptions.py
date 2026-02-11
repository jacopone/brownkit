"""Custom exceptions for BrownKit.

Provides a clear exception hierarchy with actionable error messages.
"""

from pathlib import Path


class BrownfieldError(Exception):
    """Base exception for all BrownKit errors."""

    def __init__(self, message: str, suggestion: str | None = None):
        """Initialize error with message and optional suggestion.

        Args:
            message: Human-readable error description
            suggestion: Actionable suggestion for fixing the error
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)

    def __str__(self) -> str:
        """Format error with suggestion if available."""
        if self.suggestion:
            return f"{self.message}\n\nSuggestion: {self.suggestion}"
        return self.message


class StateError(BrownfieldError):
    """Error related to workflow state management."""


class StateNotFoundError(StateError):
    """State file not found - assessment not yet run."""

    def __init__(self, state_path: Path):
        super().__init__(
            f"State file not found: {state_path}",
            "Run 'brownfield assess' to initialize the workflow",
        )
        self.state_path = state_path


class InvalidStateError(StateError):
    """State file is corrupted or has invalid schema."""

    def __init__(self, state_path: Path, reason: str):
        super().__init__(
            f"Invalid state file: {state_path}\nReason: {reason}",
            "Delete the state file and run 'brownfield assess' to re-initialize",
        )
        self.state_path = state_path
        self.reason = reason


class PhaseError(BrownfieldError):
    """Error related to phase transitions or validation."""


class PhaseTransitionError(PhaseError):
    """Invalid phase transition attempted."""

    def __init__(self, current_phase: str, requested_phase: str):
        super().__init__(
            f"Cannot transition from {current_phase} to {requested_phase}",
            f"Complete {current_phase} phase first or use 'brownfield resume' to continue",
        )
        self.current_phase = current_phase
        self.requested_phase = requested_phase


class PhasePreconditionError(PhaseError):
    """Phase preconditions not met."""

    def __init__(self, phase: str, missing_prerequisites: list[str]):
        prereqs = "\n  - ".join(missing_prerequisites)
        super().__init__(
            f"Cannot start {phase} phase - missing prerequisites:\n  - {prereqs}",
            f"Complete the required prerequisites before running 'brownfield {phase}'",
        )
        self.phase = phase
        self.missing_prerequisites = missing_prerequisites


class WorkflowPhaseError(PhaseError):
    """Workflow phase execution error."""


class LanguageDetectionError(BrownfieldError):
    """Error detecting project language or framework."""

    def __init__(self, reason: str):
        super().__init__(
            f"Language detection failed: {reason}",
            "Use --language flag to manually specify language (python/javascript/rust/go)",
        )


class ToolNotFoundError(BrownfieldError):
    """Required external tool not found in PATH."""

    def __init__(self, tool: str, install_instructions: str | None = None):
        suggestion = install_instructions or f"Install {tool} and ensure it's in your PATH"
        super().__init__(f"Required tool not found: {tool}", suggestion)
        self.tool = tool


class ValidationError(BrownfieldError):
    """Validation check failed."""


class GateValidationError(ValidationError):
    """Readiness gate validation failed."""

    def __init__(self, gate_name: str, current_value: float, threshold: float):
        super().__init__(
            f"Gate '{gate_name}' failed validation: {current_value:.2f} < {threshold:.2f}",
            f"Improve {gate_name.lower().replace('_', ' ')} to meet threshold",
        )
        self.gate_name = gate_name
        self.current_value = current_value
        self.threshold = threshold


class StructureValidationError(ValidationError):
    """Project structure validation failed."""

    def __init__(self, issues: list[str]):
        issues_list = "\n  - ".join(issues)
        super().__init__(
            f"Structure validation failed:\n  - {issues_list}",
            "Review the structure verification report and use IDE refactoring tools to fix issues",
        )
        self.issues = issues


class MetricsCollectionError(BrownfieldError):
    """Error collecting metrics."""

    def __init__(self, metric_name: str, reason: str):
        super().__init__(
            f"Failed to collect {metric_name} metric: {reason}",
            "Ensure required tools are installed and project is in valid state",
        )
        self.metric_name = metric_name
        self.reason = reason


class ConfigurationError(BrownfieldError):
    """Error in configuration."""


class InvalidConfigError(ConfigurationError):
    """Invalid configuration file or value."""

    def __init__(self, config_path: Path | None, reason: str):
        path_str = str(config_path) if config_path else "configuration"
        super().__init__(
            f"Invalid {path_str}: {reason}",
            "Check configuration syntax and values",
        )
        self.config_path = config_path
        self.reason = reason


class EnvironmentVariableError(ConfigurationError):
    """Invalid environment variable value."""

    def __init__(self, var_name: str, invalid_value: str, valid_values: list[str]):
        valid = ", ".join(valid_values)
        super().__init__(
            f"Invalid value for {var_name}: '{invalid_value}'",
            f"Valid values: {valid}",
        )
        self.var_name = var_name
        self.invalid_value = invalid_value
        self.valid_values = valid_values


class CheckpointError(BrownfieldError):
    """Error related to checkpoints."""


class CheckpointNotFoundError(CheckpointError):
    """No checkpoint found for resumption."""

    def __init__(self, phase: str | None = None):
        phase_str = f" for phase '{phase}'" if phase else ""
        super().__init__(
            f"No checkpoint found{phase_str}",
            "Run the phase command to start from the beginning",
        )
        self.phase = phase


class CheckpointCorruptedError(CheckpointError):
    """Checkpoint file is corrupted."""

    def __init__(self, checkpoint_path: Path):
        super().__init__(
            f"Checkpoint corrupted: {checkpoint_path}",
            "Use 'brownfield resume --restart' to clear and restart",
        )
        self.checkpoint_path = checkpoint_path


class GitError(BrownfieldError):
    """Error related to git operations."""


class GitNotFoundError(GitError):
    """Git repository not found."""

    def __init__(self, project_root: Path):
        super().__init__(
            f"Not a git repository: {project_root}",
            "Initialize git repository: git init",
        )
        self.project_root = project_root


class GitDirtyWorkingTreeError(GitError):
    """Git working tree has uncommitted changes."""

    def __init__(self, uncommitted_files: list[str]):
        files = "\n  - ".join(uncommitted_files[:5])
        more = f"\n  ... and {len(uncommitted_files) - 5} more" if len(uncommitted_files) > 5 else ""
        super().__init__(
            f"Uncommitted changes in working tree:\n  - {files}{more}",
            "Commit or stash changes before running brownfield commands",
        )
        self.uncommitted_files = uncommitted_files


class FileSystemError(BrownfieldError):
    """Error related to file system operations."""


class PermissionError(FileSystemError):
    """Permission denied for file operation."""

    def __init__(self, path: Path, operation: str):
        super().__init__(
            f"Permission denied for {operation}: {path}",
            f"Check file permissions: chmod u+w {path}",
        )
        self.path = path
        self.operation = operation


class DiskSpaceError(FileSystemError):
    """Insufficient disk space."""

    def __init__(self, required_mb: int, available_mb: int):
        super().__init__(
            f"Insufficient disk space: {available_mb}MB available, {required_mb}MB required",
            "Free up disk space or use a different location with BROWNFIELD_STATE_DIR",
        )
        self.required_mb = required_mb
        self.available_mb = available_mb

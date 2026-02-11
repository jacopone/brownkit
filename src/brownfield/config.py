"""Environment configuration for BrownKit.

Supports environment variables:
- BROWNFIELD_PROJECT_ROOT: Override project root directory
- BROWNFIELD_STATE_DIR: Override state directory (default: .specify/memory)
- BROWNFIELD_REPORTS_DIR: Override reports directory (default: .specify/memory)
- BROWNFIELD_TEMPLATES_DIR: Override templates directory
- BROWNFIELD_DEBUG: Enable debug logging (true/false)
- BROWNFIELD_ANALYSIS_MODE: Default analysis mode (quick/full)
- BROWNFIELD_FORCE_LANGUAGE: Force language detection override
"""

import os
from pathlib import Path


class BrownfieldConfig:
    """Configuration manager for BrownKit."""

    @staticmethod
    def get_project_root() -> Path:
        """Get project root directory.

        Returns:
            Project root path from BROWNFIELD_PROJECT_ROOT env var or current directory
        """
        root = os.environ.get("BROWNFIELD_PROJECT_ROOT")
        return Path(root).resolve() if root else Path.cwd()

    @staticmethod
    def get_state_dir(project_root: Path | None = None) -> Path:
        """Get state directory path.

        Args:
            project_root: Project root directory (defaults to configured root)

        Returns:
            State directory path
        """
        if state_dir := os.environ.get("BROWNFIELD_STATE_DIR"):
            return Path(state_dir).resolve()

        root = project_root or BrownfieldConfig.get_project_root()
        return root / ".specify" / "memory"

    @staticmethod
    def get_reports_dir(project_root: Path | None = None) -> Path:
        """Get reports directory path.

        Args:
            project_root: Project root directory (defaults to configured root)

        Returns:
            Reports directory path
        """
        if reports_dir := os.environ.get("BROWNFIELD_REPORTS_DIR"):
            return Path(reports_dir).resolve()

        root = project_root or BrownfieldConfig.get_project_root()
        return root / ".specify" / "memory"

    @staticmethod
    def get_templates_dir() -> Path | None:
        """Get custom templates directory.

        Returns:
            Templates directory path if BROWNFIELD_TEMPLATES_DIR is set, else None
        """
        if templates_dir := os.environ.get("BROWNFIELD_TEMPLATES_DIR"):
            return Path(templates_dir).resolve()
        return None

    @staticmethod
    def is_debug_enabled() -> bool:
        """Check if debug mode is enabled.

        Returns:
            True if BROWNFIELD_DEBUG is set to 'true' or '1'
        """
        debug = os.environ.get("BROWNFIELD_DEBUG", "").lower()
        return debug in ("true", "1", "yes")

    @staticmethod
    def get_default_analysis_mode() -> str:
        """Get default analysis mode.

        Returns:
            Analysis mode ('quick' or 'full'), defaults to 'quick'
        """
        mode = os.environ.get("BROWNFIELD_ANALYSIS_MODE", "quick").lower()
        return mode if mode in ("quick", "full") else "quick"

    @staticmethod
    def get_forced_language() -> str | None:
        """Get forced language override.

        Returns:
            Language name if BROWNFIELD_FORCE_LANGUAGE is set, else None
        """
        lang = os.environ.get("BROWNFIELD_FORCE_LANGUAGE")
        if lang:
            lang_lower = lang.lower()
            if lang_lower in ("python", "javascript", "rust", "go"):
                return lang_lower
        return None

    @staticmethod
    def get_state_path(project_root: Path | None = None) -> Path:
        """Get full path to state file (Spec-Kit compatible).

        Args:
            project_root: Project root directory (defaults to configured root)

        Returns:
            Full path to state.json (post-migration Spec-Kit compatible name)
        """
        state_dir = BrownfieldConfig.get_state_dir(project_root)
        return state_dir / "state.json"

    @staticmethod
    def get_checkpoint_dir(project_root: Path | None = None) -> Path:
        """Get checkpoint directory path.

        Args:
            project_root: Project root directory (defaults to configured root)

        Returns:
            Checkpoint directory path
        """
        state_dir = BrownfieldConfig.get_state_dir(project_root)
        return state_dir / "checkpoints"

    @staticmethod
    def ensure_directories(project_root: Path | None = None) -> None:
        """Ensure required directories exist.

        Args:
            project_root: Project root directory (defaults to configured root)
        """
        state_dir = BrownfieldConfig.get_state_dir(project_root)
        state_dir.mkdir(parents=True, exist_ok=True)

        reports_dir = BrownfieldConfig.get_reports_dir(project_root)
        reports_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_dir = BrownfieldConfig.get_checkpoint_dir(project_root)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

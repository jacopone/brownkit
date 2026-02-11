"""Process execution utilities with NixOS/devenv awareness."""

import os
import shutil
import subprocess
from pathlib import Path


class ProcessRunner:
    """Shell-aware subprocess wrapper for language tools."""

    @staticmethod
    def _find_devenv_root(start_path: Path) -> tuple[Path, str] | None:
        """
        Walk up directory tree to find devenv.nix or flake.nix.

        Args:
            start_path: Directory to start searching from

        Returns:
            Tuple of (root_path, type) where type is "devenv" or "flake", or None
        """
        current = start_path.resolve()

        # Walk up to root, checking each directory
        while current != current.parent:
            if (current / "devenv.nix").exists():
                return (current, "devenv")
            if (current / "flake.nix").exists():
                return (current, "flake")
            current = current.parent

        # Check root directory
        if (current / "devenv.nix").exists():
            return (current, "devenv")
        if (current / "flake.nix").exists():
            return (current, "flake")

        return None

    @staticmethod
    def _detect_shell_context(cwd: str | Path | None = None) -> tuple[str, Path | None]:
        """
        Detect the current shell environment context.

        Args:
            cwd: Working directory to check for nix files

        Returns:
            Tuple of (context_type, devenv_root_path)
            context_type: One of "nix-shell", "devenv", "direnv", "venv", "devenv-available", "flake-available", "system"
            devenv_root_path: Path to directory containing devenv.nix/flake.nix if found
        """
        # Check if we're already in a Nix shell
        if os.environ.get("IN_NIX_SHELL"):
            return ("nix-shell", None)

        # Check if we're in a devenv shell
        if os.environ.get("DEVENV_ROOT"):
            devenv_root = os.environ.get("DEVENV_ROOT")
            return ("devenv", Path(devenv_root) if devenv_root else None)

        # Check if direnv is active
        if os.environ.get("DIRENV_DIR"):
            return ("direnv", None)

        # Check if venv is active
        if os.environ.get("VIRTUAL_ENV"):
            return ("venv", None)

        # Walk up directory tree to find devenv.nix or flake.nix
        if cwd:
            cwd_path = Path(cwd) if isinstance(cwd, str) else cwd
            result = ProcessRunner._find_devenv_root(cwd_path)
            if result:
                root_path, env_type = result
                if env_type == "devenv":
                    return ("devenv-available", root_path)
                # flake
                return ("flake-available", root_path)

        return ("system", None)

    @staticmethod
    def run(cmd: list[str], cwd: str | None = None, timeout: int = 300, **kwargs) -> subprocess.CompletedProcess:
        """
        Run subprocess with timeout and shell context awareness.

        Automatically wraps commands in devenv/nix if:
        - Command is not found in PATH
        - devenv.nix or flake.nix exists in project or parent directories
        - Not already in a nix/devenv shell

        Args:
            cmd: Command and arguments as list
            cwd: Working directory for the command to execute in
            timeout: Timeout in seconds
            **kwargs: Additional arguments passed to subprocess.run

        Returns:
            CompletedProcess result
        """
        command_name = cmd[0]
        context_type, devenv_root = ProcessRunner._detect_shell_context(cwd)

        # If command doesn't exist and we have a dev environment available, wrap it
        if not shutil.which(command_name):
            if context_type == "devenv-available" and shutil.which("devenv") and devenv_root:
                # Wrap in devenv shell - the shell command inherits the cwd
                cmd = ["devenv", "shell", "--"] + cmd
            elif context_type == "flake-available" and shutil.which("nix") and devenv_root:
                # Wrap in nix develop - the command inherits the cwd
                cmd = ["nix", "develop", "-c"] + cmd

        # Set default kwargs
        default_kwargs = {
            "capture_output": True,
            "text": True,
            "timeout": timeout,
        }
        default_kwargs.update(kwargs)

        return subprocess.run(cmd, cwd=cwd, **default_kwargs)

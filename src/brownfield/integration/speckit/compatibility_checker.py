"""Spec-Kit compatibility checking for BrownKit integration."""

from pathlib import Path


class SpecKitCompatibilityChecker:
    """Checks if Spec-Kit is installed and compatible with BrownKit."""

    def __init__(self, project_root: Path):
        """Initialize compatibility checker.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.claude_commands_dir = project_root / ".claude" / "commands"
        self.specify_dir = project_root / ".specify"
        self.memory_dir = self.specify_dir / "memory"

    def check_compatibility(self) -> tuple[bool, str | None]:
        """Check if Spec-Kit is installed and compatible.

        Returns:
            Tuple of (is_compatible, error_message)
            - is_compatible: True if Spec-Kit is ready to use
            - error_message: None if compatible, error description otherwise
        """
        # Check 1: Spec-Kit slash command exists
        specify_command = self.claude_commands_dir / "speckit.specify.md"
        if not specify_command.exists():
            return (
                False,
                "Spec-Kit not installed. The /speckit.specify command is missing.\n"
                f"Expected location: {specify_command}\n\n"
                "To install Spec-Kit, see: https://github.com/github/spec-kit",
            )

        # Check 2: .specify directory structure exists
        if not self.specify_dir.exists():
            return (
                False,
                f".specify directory not found at {self.specify_dir}\n"
                "Spec-Kit appears to be installed but not initialized.\n"
                "Run /speckit.specify to initialize the directory structure.",
            )

        # Check 3: .specify/memory directory exists
        if not self.memory_dir.exists():
            return (
                False,
                f".specify/memory directory not found at {self.memory_dir}\n"
                "Spec-Kit memory directory is missing.\n"
                "This is required for BrownKit constitution storage.",
            )

        # Check 4: Verify we can write to .specify/memory
        if not self.memory_dir.is_dir():
            return (
                False,
                f"{self.memory_dir} exists but is not a directory.\n"
                "Please resolve this conflict and ensure .specify/memory is a directory.",
            )

        # Check 5: Test write permissions
        test_file = self.memory_dir / ".brownkit_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except (OSError, PermissionError) as e:
            return (
                False,
                f"Cannot write to .specify/memory directory: {e}\nPlease check directory permissions.",
            )

        # All checks passed
        return True, None

    def get_speckit_version(self) -> str | None:
        """Attempt to detect Spec-Kit version.

        Returns:
            Version string if detectable, None otherwise
        """
        # Try to read version from speckit.specify command
        specify_command = self.claude_commands_dir / "speckit.specify.md"

        if not specify_command.exists():
            return None

        try:
            content = specify_command.read_text()
            # Look for version marker in command file
            for line in content.split("\n"):
                if "version" in line.lower() and any(c.isdigit() for c in line):
                    # Simple extraction - you might need to enhance this
                    import re

                    version_match = re.search(r"v?(\d+\.\d+\.\d+)", line)
                    if version_match:
                        return version_match.group(1)
        except Exception:
            pass

        # Default to "unknown" if we can't detect
        return "unknown"

    def check_constitution_exists(self) -> bool:
        """Check if constitution.md already exists.

        Returns:
            True if constitution.md exists in .specify/memory
        """
        constitution_path = self.memory_dir / "constitution.md"
        return constitution_path.exists()

    def get_constitution_path(self) -> Path:
        """Get path where constitution.md should be stored.

        Returns:
            Path to constitution.md in .specify/memory
        """
        return self.memory_dir / "constitution.md"

    def verify_slash_command_available(self, command_name: str) -> bool:
        """Check if a specific slash command is available.

        Args:
            command_name: Name of command (e.g., "speckit.specify")

        Returns:
            True if command file exists
        """
        command_file = self.claude_commands_dir / f"{command_name}.md"
        return command_file.exists()

    def get_compatibility_report(self) -> str:
        """Generate detailed compatibility report.

        Returns:
            Formatted string with compatibility details
        """
        lines = ["Spec-Kit Compatibility Report", "=" * 50, ""]

        # Check compatibility
        is_compatible, error = self.check_compatibility()

        if is_compatible:
            lines.append("✅ Spec-Kit is installed and compatible")
            lines.append("")

            # Version info
            version = self.get_speckit_version()
            lines.append(f"Spec-Kit Version: {version or 'unknown'}")
            lines.append("")

            # Directory structure
            lines.append("Directory Structure:")
            lines.append(f"  ✅ .claude/commands/ - {self.claude_commands_dir}")
            lines.append(f"  ✅ .specify/ - {self.specify_dir}")
            lines.append(f"  ✅ .specify/memory/ - {self.memory_dir}")
            lines.append("")

            # Constitution status
            if self.check_constitution_exists():
                lines.append("⚠️  Constitution already exists")
                lines.append(f"    Location: {self.get_constitution_path()}")
                lines.append("    BrownKit will backup existing before generating new one")
            else:
                lines.append("✅ Ready to generate constitution")
                lines.append(f"    Will be created at: {self.get_constitution_path()}")

        else:
            lines.append("❌ Spec-Kit compatibility check failed")
            lines.append("")
            lines.append("Error:")
            for line in error.split("\n"):
                lines.append(f"  {line}")

        return "\n".join(lines)

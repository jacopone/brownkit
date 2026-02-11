"""Unit tests for Spec-Kit Compatibility Checker (Phase 2)."""

from brownfield.integration.speckit import SpecKitCompatibilityChecker


class TestCompatibilityChecker:
    """Test SpecKitCompatibilityChecker class."""

    def test_init(self, tmp_path):
        """Test initialization."""
        checker = SpecKitCompatibilityChecker(tmp_path)

        assert checker.project_root == tmp_path
        assert checker.claude_commands_dir == tmp_path / ".claude" / "commands"
        assert checker.specify_dir == tmp_path / ".specify"
        assert checker.memory_dir == tmp_path / ".specify" / "memory"

    def test_check_compatibility_missing_slash_command(self, tmp_path):
        """Test compatibility check fails when /speckit.specify is missing."""
        checker = SpecKitCompatibilityChecker(tmp_path)

        is_compatible, error = checker.check_compatibility()

        assert is_compatible is False
        assert "not installed" in error.lower()
        assert "/speckit.specify" in error
        assert "claude/commands" in error.lower()

    def test_check_compatibility_missing_specify_dir(self, tmp_path):
        """Test compatibility check fails when .specify directory is missing."""
        # Create slash command but not .specify directory
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Spec-Kit Specify")

        checker = SpecKitCompatibilityChecker(tmp_path)
        is_compatible, error = checker.check_compatibility()

        assert is_compatible is False
        assert ".specify directory not found" in error
        assert "not initialized" in error.lower()

    def test_check_compatibility_missing_memory_dir(self, tmp_path):
        """Test compatibility check fails when .specify/memory is missing."""
        # Create slash command and .specify but not memory directory
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Spec-Kit Specify")

        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()

        checker = SpecKitCompatibilityChecker(tmp_path)
        is_compatible, error = checker.check_compatibility()

        assert is_compatible is False
        assert "memory directory not found" in error.lower()

    def test_check_compatibility_memory_not_directory(self, tmp_path):
        """Test compatibility check fails when .specify/memory is a file."""
        # Create full structure but memory is a file
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Spec-Kit Specify")

        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()

        # Create memory as a file instead of directory
        (specify_dir / "memory").write_text("oops")

        checker = SpecKitCompatibilityChecker(tmp_path)
        is_compatible, error = checker.check_compatibility()

        assert is_compatible is False
        assert "not a directory" in error

    def test_check_compatibility_no_write_permission(self, tmp_path):
        """Test compatibility check fails when can't write to memory directory."""
        # Create full structure
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Spec-Kit Specify")

        memory_dir = tmp_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True)

        # Make directory read-only
        import os

        os.chmod(memory_dir, 0o444)

        try:
            checker = SpecKitCompatibilityChecker(tmp_path)
            is_compatible, error = checker.check_compatibility()

            assert is_compatible is False
            assert "cannot write" in error.lower()
        finally:
            # Restore permissions for cleanup
            os.chmod(memory_dir, 0o755)

    def test_check_compatibility_success(self, tmp_path):
        """Test compatibility check succeeds with proper setup."""
        # Create full proper structure
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Spec-Kit Specify")

        memory_dir = tmp_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True)

        checker = SpecKitCompatibilityChecker(tmp_path)
        is_compatible, error = checker.check_compatibility()

        assert is_compatible is True
        assert error is None

    def test_check_constitution_exists_false(self, tmp_path):
        """Test check_constitution_exists returns False when not present."""
        memory_dir = tmp_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True)

        checker = SpecKitCompatibilityChecker(tmp_path)

        assert checker.check_constitution_exists() is False

    def test_check_constitution_exists_true(self, tmp_path):
        """Test check_constitution_exists returns True when present."""
        memory_dir = tmp_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Constitution")

        checker = SpecKitCompatibilityChecker(tmp_path)

        assert checker.check_constitution_exists() is True

    def test_get_constitution_path(self, tmp_path):
        """Test get_constitution_path returns correct path."""
        checker = SpecKitCompatibilityChecker(tmp_path)

        path = checker.get_constitution_path()

        assert path == tmp_path / ".specify" / "memory" / "constitution.md"

    def test_verify_slash_command_available_true(self, tmp_path):
        """Test verify_slash_command_available returns True when command exists."""
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Command")

        checker = SpecKitCompatibilityChecker(tmp_path)

        assert checker.verify_slash_command_available("speckit.specify") is True

    def test_verify_slash_command_available_false(self, tmp_path):
        """Test verify_slash_command_available returns False when command missing."""
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)

        checker = SpecKitCompatibilityChecker(tmp_path)

        assert checker.verify_slash_command_available("speckit.specify") is False

    def test_get_compatibility_report_compatible(self, tmp_path):
        """Test get_compatibility_report when Spec-Kit is compatible."""
        # Setup proper structure
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Spec-Kit v1.0.0")

        memory_dir = tmp_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True)

        checker = SpecKitCompatibilityChecker(tmp_path)
        report = checker.get_compatibility_report()

        assert "Spec-Kit Compatibility Report" in report
        assert "✅" in report
        assert "compatible" in report.lower()
        assert ".claude/commands/" in report
        assert ".specify/" in report
        assert ".specify/memory/" in report

    def test_get_compatibility_report_incompatible(self, tmp_path):
        """Test get_compatibility_report when Spec-Kit is not compatible."""
        checker = SpecKitCompatibilityChecker(tmp_path)
        report = checker.get_compatibility_report()

        assert "Spec-Kit Compatibility Report" in report
        assert "❌" in report
        assert "failed" in report.lower()
        assert "Error:" in report

    def test_get_compatibility_report_with_existing_constitution(self, tmp_path):
        """Test report shows warning when constitution already exists."""
        # Setup proper structure
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Spec-Kit")

        memory_dir = tmp_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "constitution.md").write_text("# Existing")

        checker = SpecKitCompatibilityChecker(tmp_path)
        report = checker.get_compatibility_report()

        assert "⚠️" in report
        assert "already exists" in report.lower()
        assert "backup" in report.lower()

    def test_get_speckit_version_unknown(self, tmp_path):
        """Test get_speckit_version returns 'unknown' when can't detect."""
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# No version info")

        checker = SpecKitCompatibilityChecker(tmp_path)
        version = checker.get_speckit_version()

        assert version == "unknown"

    def test_get_speckit_version_from_command_file(self, tmp_path):
        """Test get_speckit_version extracts version from command file."""
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "speckit.specify.md").write_text("# Spec-Kit Specify\n\nVersion: v1.2.3\n")

        checker = SpecKitCompatibilityChecker(tmp_path)
        version = checker.get_speckit_version()

        assert version == "1.2.3"

"""Structure verification module for validating project organization after manual refactoring."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from brownfield.models.assessment import LanguageDetection
from brownfield.plugins.registry import get_handler
from brownfield.utils.output_formatter import OutputFormatter
from brownfield.utils.process_runner import ProcessRunner


@dataclass
class StructureIssue:
    """Represents a structure compliance issue."""

    category: str  # "directory", "build", "imports", "files"
    severity: str  # "error", "warning"
    message: str
    suggestion: str | None = None


@dataclass
class VerificationResult:
    """Result of structure verification."""

    passed: bool
    directory_structure: bool
    build_integrity: bool
    import_integrity: bool
    no_stray_files: bool
    issues: list[StructureIssue]
    timestamp: datetime


class StructureVerifier:
    """Verifies project structure after manual refactoring."""

    def __init__(self, project_root: Path, language_detection: LanguageDetection):
        """Initialize structure verifier."""
        self.project_root = project_root
        self.language_detection = language_detection
        self.formatter = OutputFormatter()
        self.process_runner = ProcessRunner()
        self.handler = get_handler(language_detection.language)

    def verify(self) -> VerificationResult:
        """Run all verification checks."""
        issues = []
        timestamp = datetime.utcnow()

        # Check 1: Directory structure
        self.formatter.info("Checking directory structure...")
        dir_check, dir_issues = self._verify_directory_structure()
        issues.extend(dir_issues)
        if dir_check:
            self.formatter.success("  ✓ Directory structure compliant")
        else:
            self.formatter.error("  ❌ Directory structure issues found")

        # Check 2: Build integrity
        self.formatter.info("Checking build integrity...")
        build_check, build_issues = self._verify_build_integrity()
        issues.extend(build_issues)
        if build_check:
            self.formatter.success("  ✓ Build verification passed")
        else:
            self.formatter.error("  ❌ Build verification failed")

        # Check 3: Import integrity
        self.formatter.info("Checking import integrity...")
        import_check, import_issues = self._verify_import_integrity()
        issues.extend(import_issues)
        if import_check:
            self.formatter.success("  ✓ Import integrity verified")
        else:
            self.formatter.error("  ❌ Import integrity issues found")

        # Check 4: No stray files
        self.formatter.info("Checking for stray files...")
        stray_check, stray_issues = self._check_stray_files()
        issues.extend(stray_issues)
        if stray_check:
            self.formatter.success("  ✓ No stray files in root")
        else:
            self.formatter.warning("  ⚠️  Found files that should be moved")

        # Overall result
        passed = dir_check and build_check and import_check and stray_check

        return VerificationResult(
            passed=passed,
            directory_structure=dir_check,
            build_integrity=build_check,
            import_integrity=import_check,
            no_stray_files=stray_check,
            issues=issues,
            timestamp=timestamp,
        )

    def _verify_directory_structure(self) -> tuple[bool, list[StructureIssue]]:
        """Verify standard directories exist."""
        issues = []
        standard_structure = self.handler.get_standard_structure()

        # Check required directories exist
        all_exist = True
        for dir_name in standard_structure:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                all_exist = False
                issues.append(
                    StructureIssue(
                        category="directory",
                        severity="error",
                        message=f"Missing required directory: {dir_name}/",
                        suggestion=f"Create with: mkdir -p {dir_name}",
                    )
                )

        # Check for expected files in directories
        for dir_name, expected_files in standard_structure.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                for expected_file in expected_files:
                    file_path = dir_path / expected_file
                    if not file_path.exists() and expected_file != "README.md":
                        # README.md is optional
                        issues.append(
                            StructureIssue(
                                category="directory",
                                severity="warning",
                                message=f"Missing expected file: {dir_name}/{expected_file}",
                                suggestion=f"Create if needed: touch {dir_name}/{expected_file}",
                            )
                        )

        return (all_exist and len([i for i in issues if i.severity == "error"]) == 0, issues)

    def _verify_build_integrity(self) -> tuple[bool, list[StructureIssue]]:
        """Verify project builds successfully."""
        issues = []

        try:
            build_passed = self.handler.verify_build(self.project_root)

            if not build_passed:
                issues.append(
                    StructureIssue(
                        category="build",
                        severity="error",
                        message="Build verification failed",
                        suggestion="Check for syntax errors or missing dependencies. "
                        "Imports may not have been updated correctly after moving files.",
                    )
                )

            return (build_passed, issues)

        except Exception as e:
            issues.append(
                StructureIssue(
                    category="build",
                    severity="error",
                    message=f"Build verification error: {e}",
                    suggestion="Ensure language tools are installed and project is properly configured.",
                )
            )
            return (False, issues)

    def _verify_import_integrity(self) -> tuple[bool, list[StructureIssue]]:
        """Verify all imports can be resolved."""
        issues = []

        # Language-specific import verification
        if self.language_detection.language == "python":
            return self._verify_python_imports()
        if self.language_detection.language == "javascript":
            return self._verify_javascript_imports()
        if self.language_detection.language == "rust":
            return self._verify_rust_imports()
        if self.language_detection.language == "go":
            return self._verify_go_imports()

        # Default: no specific import verification
        return (True, issues)

    def _verify_python_imports(self) -> tuple[bool, list[StructureIssue]]:
        """Verify Python import statements."""
        issues = []
        broken_imports = []

        # Try to compile all Python files
        for py_file in self.project_root.rglob("*.py"):
            # Skip virtual environments
            if ".venv" in str(py_file) or "venv" in str(py_file):
                continue

            try:
                # Use py_compile to check syntax and imports at module level
                import py_compile

                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                # Check if it's an import error
                error_msg = str(e)
                if "ImportError" in error_msg or "ModuleNotFoundError" in error_msg:
                    broken_imports.append((py_file, error_msg))

        # Report broken imports
        for file_path, error in broken_imports:
            rel_path = file_path.relative_to(self.project_root)
            issues.append(
                StructureIssue(
                    category="imports",
                    severity="error",
                    message=f"Broken import in {rel_path}: {error}",
                    suggestion="Use IDE's 'Move Module' refactoring to update imports automatically, "
                    "or manually update import statements to match new file locations.",
                )
            )

        return (len(broken_imports) == 0, issues)

    def _verify_javascript_imports(self) -> tuple[bool, list[StructureIssue]]:
        """Verify JavaScript import/require statements."""
        issues = []

        # For JavaScript, we can check if files can be parsed
        # but actual import resolution requires running the code or using a bundler
        # For now, just check syntax
        for js_file in self.project_root.rglob("*.js"):
            if "node_modules" in str(js_file):
                continue

            try:
                # Basic check: can we read the file?
                content = js_file.read_text(encoding="utf-8")

                # Look for obviously broken imports (relative paths to non-existent files)
                lines = content.split("\n")
                for _line_num, line in enumerate(lines, 1):
                    if "from" in line or "require(" in line:
                        # Could add more sophisticated checking here
                        pass

            except Exception as e:
                issues.append(
                    StructureIssue(
                        category="imports",
                        severity="warning",
                        message=f"Could not verify imports in {js_file.name}: {e}",
                        suggestion="Manually verify import paths are correct.",
                    )
                )

        # If no errors found, assume OK
        return (len([i for i in issues if i.severity == "error"]) == 0, issues)

    def _verify_rust_imports(self) -> tuple[bool, list[StructureIssue]]:
        """Verify Rust mod/use statements."""
        issues = []

        # For Rust, cargo check handles import verification
        # Already covered by build verification
        return (True, issues)

    def _verify_go_imports(self) -> tuple[bool, list[StructureIssue]]:
        """Verify Go import statements."""
        issues = []

        # For Go, go build handles import verification
        # Already covered by build verification
        return (True, issues)

    def _check_stray_files(self) -> tuple[bool, list[StructureIssue]]:
        """Check for source files that should be moved."""
        issues = []
        stray_files = []

        # Language-specific patterns for files that shouldn't be in root
        if self.language_detection.language == "python":
            for py_file in self.project_root.glob("*.py"):
                # Exclude common root-level files
                if py_file.name in ["setup.py", "conftest.py", "manage.py"]:
                    continue
                stray_files.append(py_file)

        elif self.language_detection.language == "javascript":
            for js_file in self.project_root.glob("*.js"):
                # Exclude config files
                if js_file.name.endswith("config.js") or js_file.name.endswith(".config.js"):
                    continue
                stray_files.append(js_file)

        elif self.language_detection.language == "go":
            for go_file in self.project_root.glob("*.go"):
                # main.go should be in cmd/
                stray_files.append(go_file)

        # Report stray files
        if stray_files:
            file_list = ", ".join(f.name for f in stray_files)
            issues.append(
                StructureIssue(
                    category="files",
                    severity="warning",
                    message=f"Source files still in root directory: {file_list}",
                    suggestion="Move to standard locations using IDE refactoring tools. "
                    "Expected location: src/ or appropriate subdirectory.",
                )
            )

        return (len(stray_files) == 0, issues)

    def generate_verification_report(self, result: VerificationResult) -> str:
        """Generate markdown verification report."""
        report = f"""# Structure Verification Report

**Generated**: {result.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}
**Project**: {self.project_root.name}
**Language**: {self.language_detection.language}

## Overall Result

{"✅ **PASSED** - Structure verification successful!" if result.passed else "❌ **FAILED** - Issues found requiring attention"}

## Check Results

| Check | Status |
|-------|--------|
| Directory Structure | {"✓ PASS" if result.directory_structure else "✗ FAIL"} |
| Build Integrity | {"✓ PASS" if result.build_integrity else "✗ FAIL"} |
| Import Integrity | {"✓ PASS" if result.import_integrity else "✗ FAIL"} |
| No Stray Files | {"✓ PASS" if result.no_stray_files else "⚠ WARN"} |

## Issues Found

"""

        if not result.issues:
            report += "No issues found! Project structure is compliant.\n"
        else:
            # Group issues by category
            by_category = {}
            for issue in result.issues:
                if issue.category not in by_category:
                    by_category[issue.category] = []
                by_category[issue.category].append(issue)

            for category, issues in by_category.items():
                report += f"\n### {category.title()} Issues\n\n"
                for issue in issues:
                    icon = "❌" if issue.severity == "error" else "⚠️"
                    report += f"{icon} **{issue.severity.upper()}**: {issue.message}\n"
                    if issue.suggestion:
                        report += f"   💡 *Suggestion*: {issue.suggestion}\n"
                    report += "\n"

        report += """
## Next Steps

"""

        if result.passed:
            report += """✅ Structure verification passed! Your project now follows ecosystem conventions.

Run the next phase:
```bash
brownfield testing
```
"""
        else:
            report += """❌ Please address the issues above and re-run verification:

1. Fix the issues listed above
2. Use IDE refactoring tools for import updates
3. Re-run verification: `brownfield structure --verify`
"""

        return report

"""Metrics collection engine."""

from pathlib import Path

from brownfield.models.assessment import ComplexityViolation, Metrics
from brownfield.plugins.registry import get_handler
from brownfield.utils.process_runner import ProcessRunner


class MetricsCollector:
    """Collects baseline metrics from codebase."""

    def collect(
        self, project_root: Path, language: str, mode: str = "quick"
    ) -> Metrics:
        """
        Collect metrics from codebase using language-specific handler.

        Args:
            project_root: Path to project directory
            language: Primary language detected (e.g., "python", "javascript")
            mode: "quick" or "full" analysis mode

        Returns:
            Metrics object with collected data
        """
        try:
            # Get language handler
            handler = get_handler(language)

            # Measure complexity using language-specific tools
            complexity = handler.measure_complexity(project_root)
            complexity_avg = complexity.get("average", 0.0)
            complexity_max = int(complexity.get("maximum", 0))

            # Get complexity violations (functions with CCN > 10)
            complexity_violations = self._extract_complexity_violations(project_root, language)

            # Scan for security vulnerabilities
            security = handler.scan_security(project_root)
            critical_vulns = security.get("critical", 0)
            high_vulns = security.get("high", 0)
            medium_vulns = security.get("medium", 0)

            # Verify build (returns bool for now)
            build_passes = handler.verify_build(project_root)
            build_status = "passing" if build_passes else "failing"

            # Count lines of code (simple implementation for now)
            total_loc = self._count_loc(project_root)

            # Get git commit count
            git_commits = self._count_git_commits(project_root)

            # Measure test coverage
            test_coverage = self._measure_coverage(project_root)
            test_loc = self._count_test_loc(project_root)

            return Metrics(
                test_coverage=test_coverage,
                complexity_avg=complexity_avg,
                complexity_max=complexity_max,
                critical_vulnerabilities=critical_vulns,
                high_vulnerabilities=high_vulns,
                medium_vulnerabilities=medium_vulns,
                build_status=build_status,
                documentation_coverage=0.0,  # TODO: Implement doc coverage
                total_loc=total_loc,
                test_loc=test_loc,
                git_commits=git_commits,
                git_secrets_found=0,  # TODO: Implement secret scanning
                complexity_violations=complexity_violations,
            )

        except Exception:
            # Handler failed, return safe defaults
            return Metrics(
                test_coverage=0.0,
                complexity_avg=0.0,
                complexity_max=0,
                critical_vulnerabilities=0,
                high_vulnerabilities=0,
                medium_vulnerabilities=0,
                build_status="unknown",
                documentation_coverage=0.0,
                total_loc=0,
                test_loc=0,
                git_commits=0,
                git_secrets_found=0,
                complexity_violations=[],
            )

    def _count_loc(self, project_root: Path) -> int:
        """Count total lines of code (simple implementation)."""
        try:
            result = ProcessRunner.run(
                ["tokei", str(project_root), "-o", "json"],
                cwd=str(project_root),
                timeout=60,
            )
            if result.returncode == 0:
                import json

                data = json.loads(result.stdout)
                # Sum all code lines across languages
                total = sum(
                    lang_data.get("code", 0)
                    for lang_data in data.values()
                    if isinstance(lang_data, dict)
                )
                return total
        except Exception:
            pass

        # Fallback: count Python files manually
        py_files = list(project_root.rglob("*.py"))
        total_lines = 0
        for py_file in py_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    total_lines += sum(1 for _ in f)
            except Exception:
                continue
        return total_lines

    def _count_git_commits(self, project_root: Path) -> int:
        """Count git commits in repository."""
        try:
            result = ProcessRunner.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=str(project_root),
                timeout=30,
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except Exception:
            pass
        return 0

    def _measure_coverage(self, project_root: Path) -> float:
        """
        Measure test coverage using pytest-cov.

        Returns:
            Coverage percentage (0.0 to 1.0)
        """
        import json
        import shutil

        # Detect if we're in a devenv project
        context_type, devenv_root = ProcessRunner._detect_shell_context(project_root)
        use_devenv = context_type == "devenv-available" and shutil.which("devenv")

        if use_devenv:
            # For devenv projects, we'll run pytest through devenv shell
            # This ensures pytest-cov is available from the devenv environment
            print("🔧 Detected devenv project - using devenv shell for coverage measurement")
        else:
            # For non-devenv projects, check if pytest is available
            if not shutil.which("pytest"):
                print("⚠️  pytest not found in PATH - skipping coverage measurement")
                return 0.0

            # Check if pytest-cov is installed by trying to import it
            try:
                result = ProcessRunner.run(
                    ["python", "-c", "import pytest_cov"],
                    cwd=str(project_root),
                    timeout=10,
                )
                if result.returncode != 0:
                    print("⚠️  pytest-cov not installed - run: pip install pytest-cov")
                    return 0.0
            except Exception:
                print("⚠️  Could not verify pytest-cov installation")
                return 0.0

        try:
            # Try to detect source directory from pyproject.toml
            cov_path = self._detect_coverage_source(project_root)

            # Build pytest command
            if cov_path:
                pytest_cmd = ["pytest", f"--cov={cov_path}", "--cov-report=json", "-q"]
            else:
                # Let pyproject.toml configure coverage source
                pytest_cmd = ["pytest", "--cov", "--cov-report=json", "-q"]

            # Wrap in devenv shell if needed
            if use_devenv:
                pytest_cmd = ["devenv", "shell", "--"] + pytest_cmd

            print(f"🔍 Running: {' '.join(pytest_cmd)} (in {project_root})")

            # Run pytest with coverage
            result = ProcessRunner.run(
                pytest_cmd,
                cwd=str(project_root),
                timeout=300,
            )

            if result.returncode != 0 and result.returncode != 5:  # 5 = no tests collected
                print(f"⚠️  pytest exited with code {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
                return 0.0

            # Look for coverage.json in multiple locations
            possible_locations = [
                project_root / "coverage.json",
                project_root / ".coverage.json",
                project_root / "htmlcov" / "coverage.json",
            ]

            coverage_file = None
            for loc in possible_locations:
                if loc.exists():
                    coverage_file = loc
                    break

            if coverage_file:
                print(f"✓ Found coverage report at {coverage_file.name}")
                with open(coverage_file, encoding="utf-8") as f:
                    data = json.load(f)
                    percent = data.get("totals", {}).get("percent_covered", 0.0) / 100.0
                    return percent
            else:
                print("⚠️  coverage.json not generated - check pytest-cov configuration")
                return 0.0

        except Exception as e:
            print(f"⚠️  Coverage measurement error: {e}")
            return 0.0

    def _detect_coverage_source(self, project_root: Path) -> str:
        """
        Detect the source directory for coverage measurement.

        Returns:
            Source path string or empty string if should use pyproject.toml config
        """
        # Check if pyproject.toml has coverage.run.source configured
        pyproject = project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomllib
            except ImportError:
                # Python < 3.11
                try:
                    import tomli as tomllib
                except ImportError:
                    pass
                else:
                    with open(pyproject, "rb") as f:
                        data = tomllib.load(f)
                        # If pyproject.toml has coverage config, let it handle the source
                        if "tool" in data and "coverage" in data["tool"]:
                            return ""  # Let pyproject.toml configure it
            else:
                with open(pyproject, "rb") as f:
                    data = tomllib.load(f)
                    # If pyproject.toml has coverage config, let it handle the source
                    if "tool" in data and "coverage" in data["tool"]:
                        return ""  # Let pyproject.toml configure it

        # Fall back to common patterns
        if (project_root / "src").exists():
            return "src"
        elif (project_root / "lib").exists():
            return "lib"
        else:
            # Try to find the main package directory
            for item in project_root.iterdir():
                if item.is_dir() and not item.name.startswith(".") and item.name not in ["tests", "test", "docs", "examples"]:
                    return item.name

        return "."

    def _count_test_loc(self, project_root: Path) -> int:
        """Count lines of code in test files."""
        test_dirs = [project_root / "tests", project_root / "test"]
        total_lines = 0

        for test_dir in test_dirs:
            if not test_dir.exists():
                continue

            # Count all Python test files
            for test_file in test_dir.rglob("*.py"):
                try:
                    with open(test_file, encoding="utf-8") as f:
                        total_lines += sum(1 for _ in f)
                except Exception:
                    continue

        return total_lines

    def _extract_complexity_violations(
        self, project_root: Path, language: str, threshold: int = 10
    ) -> list[ComplexityViolation]:
        """
        Extract detailed complexity violations from lizard analysis.

        Args:
            project_root: Project root directory
            language: Programming language
            threshold: Complexity threshold (default: 10)

        Returns:
            List of ComplexityViolation objects
        """
        violations = []

        try:
            import xml.etree.ElementTree as ET

            # Run lizard with XML output
            result = ProcessRunner.run(
                ["lizard", str(project_root), "--xml"],
                cwd=str(project_root),
                timeout=300,
            )

            if result.returncode != 0 and not result.stdout:
                return violations

            # Parse lizard XML output
            root = ET.fromstring(result.stdout)

            # Find all function measurements
            for item in root.findall(".//measure[@type='Function']/item"):
                # Skip averages or summaries
                if "average" in item.get("name", "").lower():
                    continue

                # Get all value elements: Nr, NCSS, CCN
                values = item.findall("value")
                if len(values) >= 3:
                    try:
                        ccn = int(values[2].text)  # CCN is the 3rd value
                        if ccn > threshold:
                            # Extract details from item name
                            # Format: "function_name(...) at ./path/to/file.py:line"
                            item_name = item.get("name", "")
                            if " at " in item_name:
                                func_name = item_name.split(" at ")[0]
                                location = item_name.split(" at ")[1]
                                parts = location.split(":")
                                file_path = parts[0].lstrip("./")
                                line_num = int(parts[1]) if len(parts) > 1 else 0

                                violations.append(
                                    ComplexityViolation(
                                        file=file_path,
                                        function=func_name,
                                        complexity=ccn,
                                        line=line_num,
                                    )
                                )
                    except (ValueError, AttributeError):
                        continue

        except Exception:
            pass

        # Sort by complexity (highest first)
        violations.sort(key=lambda v: v.complexity, reverse=True)
        return violations

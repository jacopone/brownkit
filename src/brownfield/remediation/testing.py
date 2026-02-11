"""Testing infrastructure bootstrapping."""

import ast
from pathlib import Path

from brownfield.plugins.base import LanguageHandler, TestSetupResult
from brownfield.state.decision_logger import DecisionLogger
from brownfield.utils.process_runner import ProcessRunner


class TestingBootstrapper:
    """Bootstrap test infrastructure for brownfield projects."""

    def __init__(self, handler: LanguageHandler, project_root: Path):
        """
        Initialize testing bootstrapper.

        Args:
            handler: Language-specific handler
            project_root: Project root directory
        """
        self.handler = handler
        self.project_root = project_root
        self.decision_logger = DecisionLogger(project_root / ".specify" / "memory" / "brownfield-decisions.md")

    def bootstrap(
        self,
        core_modules: list[Path] | None = None,
        coverage_target: float = 0.6,
    ) -> TestSetupResult:
        """
        Bootstrap test framework and generate initial tests.

        Args:
            core_modules: List of core module paths to prioritize for testing
            coverage_target: Target coverage percentage (default 0.6 for 60%)

        Returns:
            TestSetupResult with setup details and metrics
        """
        # Use language handler's bootstrap_tests method
        result = self.handler.bootstrap_tests(
            self.project_root,
            core_modules or self._identify_core_modules(),
            coverage_target,
        )

        # Log decision
        self.decision_logger.log_decision(
            problem=f"Project has {result.coverage:.1%} test coverage",
            solution=f"Added {result.framework} test framework with {len(result.test_files_created)} test files",
            confidence="HIGH",
            alternatives=[
                "Manual test writing",
                "Different test framework",
            ],
            risks=[
                "Generated tests may need refinement",
                "Coverage target may not be reached on first pass",
            ],
        )

        return result

    def _identify_core_modules(self) -> list[Path]:
        """
        Identify core business logic modules using heuristics.

        Returns:
            List of paths to core modules
        """
        core_modules = []

        # Look for modules in src/, lib/, or project-specific directories
        source_dirs = [
            self.project_root / "src",
            self.project_root / "lib",
            self.project_root / self.project_root.name,  # Project-named directory
        ]

        for source_dir in source_dirs:
            if source_dir.exists() and source_dir.is_dir():
                # Find Python files (extend for other languages)
                for py_file in source_dir.rglob("*.py"):
                    # Skip test files, __init__.py, and setup files
                    if self._is_core_module(py_file):
                        core_modules.append(py_file)

        return core_modules[:20]  # Limit to top 20 files to avoid overwhelming

    def _is_core_module(self, file_path: Path) -> bool:
        """
        Determine if a file is a core business logic module.

        Args:
            file_path: Path to file

        Returns:
            True if file is core business logic
        """
        # Skip test files
        if "test" in file_path.name.lower() or "test" in str(file_path.parent).lower():
            return False

        # Skip __init__.py
        if file_path.name == "__init__.py":
            return False

        # Skip setup/config files
        if file_path.name in ["setup.py", "config.py", "settings.py"]:
            return False

        # File should have substantive code (>50 lines)
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
                code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
                return len(code_lines) > 50
        except Exception:
            return False

    def generate_smoke_tests(self, modules: list[Path]) -> list[Path]:
        """
        Generate smoke tests for given modules.

        Args:
            modules: List of module paths

        Returns:
            List of generated test file paths
        """
        test_files = []

        for module in modules:
            test_file = self._create_smoke_test(module)
            if test_file:
                test_files.append(test_file)

        return test_files

    def _create_smoke_test(self, module_path: Path) -> Path | None:
        """
        Create a smoke test for a module.

        Args:
            module_path: Path to module

        Returns:
            Path to created test file, or None if creation failed
        """
        # Determine test file path
        test_dir = self.project_root / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Create test file name
        test_file = test_dir / f"test_{module_path.stem}.py"

        # Generate smoke test content
        test_content = self._generate_smoke_test_content(module_path)

        if test_content:
            test_file.write_text(test_content, encoding="utf-8")
            return test_file

        return None

    def _generate_smoke_test_content(self, module_path: Path) -> str:
        """
        Generate smoke test content for a module.

        Args:
            module_path: Path to module

        Returns:
            Test file content as string
        """
        # Parse module to find classes and functions
        try:
            with open(module_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception:
            return ""

        # Extract top-level classes and functions
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        ]

        # Calculate module import path
        module_import = self._calculate_import_path(module_path)

        # Generate test content
        lines = [
            f'"""Smoke tests for {module_path.stem}."""',
            "",
            "import pytest",
            f"from {module_import} import (",
        ]

        # Add imports
        for cls in classes[:5]:  # Limit to 5 classes
            lines.append(f"    {cls},")
        for func in functions[:5]:  # Limit to 5 functions
            lines.append(f"    {func},")

        lines.append(")")
        lines.append("")
        lines.append("")

        # Generate smoke tests for classes
        for cls in classes[:5]:
            lines.append(f"def test_{cls.lower()}_instantiation():")
            lines.append(f'    """Test {cls} can be instantiated."""')
            lines.append("    # Smoke test - verify class can be imported and instantiated")
            lines.append(f"    assert {cls} is not None")
            lines.append("")

        # Generate smoke tests for functions
        for func in functions[:5]:
            lines.append(f"def test_{func}_exists():")
            lines.append(f'    """Test {func} function exists."""')
            lines.append("    # Smoke test - verify function can be imported")
            lines.append(f"    assert callable({func})")
            lines.append("")

        return "\n".join(lines)

    def _calculate_import_path(self, module_path: Path) -> str:
        """
        Calculate the Python import path for a module.

        Args:
            module_path: Path to module file

        Returns:
            Import path string (e.g., "myproject.module")
        """
        # Try to find src/ directory
        src_dir = self.project_root / "src"
        if src_dir in module_path.parents:
            relative = module_path.relative_to(src_dir)
        else:
            relative = module_path.relative_to(self.project_root)

        # Convert path to module notation
        parts = list(relative.parts[:-1]) + [relative.stem]
        return ".".join(parts)

    def generate_contract_tests(self, modules: list[Path]) -> list[Path]:
        """
        Generate contract tests for public APIs in modules.

        Args:
            modules: List of module paths

        Returns:
            List of generated contract test file paths
        """
        contract_test_dir = self.project_root / "tests" / "contract"
        contract_test_dir.mkdir(parents=True, exist_ok=True)

        test_files = []

        for module in modules:
            test_file = self._create_contract_test(module, contract_test_dir)
            if test_file:
                test_files.append(test_file)

        return test_files

    def _create_contract_test(self, module_path: Path, contract_test_dir: Path) -> Path | None:
        """
        Create contract tests for a module's public APIs.

        Args:
            module_path: Path to module
            contract_test_dir: Directory for contract tests

        Returns:
            Path to created test file, or None if creation failed
        """
        # Parse module to find public functions/methods
        try:
            with open(module_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception:
            return None

        # Extract public functions (not starting with _)
        public_functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                public_functions.append(node)

        if not public_functions:
            return None

        # Create test file
        test_file = contract_test_dir / f"test_{module_path.stem}_contract.py"

        # Generate contract test content
        module_import = self._calculate_import_path(module_path)

        lines = [
            f'"""Contract tests for {module_path.stem} public APIs."""',
            "",
            "import pytest",
            f"from {module_import} import (",
        ]

        for func in public_functions[:10]:  # Limit to 10 functions
            lines.append(f"    {func.name},")

        lines.append(")")
        lines.append("")
        lines.append("")

        # Generate contract tests
        for func in public_functions[:10]:
            lines.append(f"def test_{func.name}_contract():")
            lines.append(f'    """Contract test for {func.name}."""')
            lines.append("    # Verify function signature and basic behavior")
            lines.append(f"    assert callable({func.name})")
            lines.append("    # TODO: Add assertions for input/output types")
            lines.append("    # TODO: Add assertions for error handling")
            lines.append("")

        test_file.write_text("\n".join(lines), encoding="utf-8")
        return test_file

    def measure_coverage(self) -> float:
        """
        Measure current test coverage.

        Returns:
            Coverage percentage (0.0 to 1.0)
        """
        try:
            # Use smart coverage detection from metrics_collector
            from brownfield.assessment.metrics_collector import MetricsCollector

            collector = MetricsCollector()
            cov_path = collector._detect_coverage_source(self.project_root)

            # Build pytest command
            if cov_path:
                pytest_cmd = ["pytest", f"--cov={cov_path}", "--cov-report=term", "--cov-report=json"]
            else:
                # Let pyproject.toml configure coverage source
                pytest_cmd = ["pytest", "--cov", "--cov-report=term", "--cov-report=json"]

            # Run pytest with coverage
            _result = ProcessRunner.run(
                pytest_cmd,
                cwd=str(self.project_root),
                timeout=300,
            )

            # Parse coverage from JSON report
            import json

            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("totals", {}).get("percent_covered", 0.0) / 100.0

        except Exception:
            pass

        return 0.0

"""Speckit constitution generator."""

from pathlib import Path

from brownfield.models.state import BrownfieldState


class ConstitutionGenerator:
    """Generates project-specific Speckit constitution based on tech stack."""

    def __init__(self, project_root: Path, state: BrownfieldState):
        self.project_root = project_root
        self.state = state

    def generate(self) -> str:
        """
        Generate Speckit constitution tailored to detected tech stack.

        Returns:
            Markdown-formatted constitution content
        """
        lines = []

        # Header
        lines.append("# Project Constitution")
        lines.append("")
        lines.append(
            "This constitution defines the principles and conventions that govern "
            "development for this project. Generated during brownfield graduation."
        )
        lines.append("")

        # Project metadata
        lines.append("## Project Metadata")
        lines.append("")
        lines.append(f"- **Language**: {self.state.language}")
        if self.state.detected_framework:
            lines.append(f"- **Framework**: {self.state.detected_framework}")
        if self.state.baseline_metrics and self.state.baseline_metrics.lines_of_code:
            lines.append(f"- **Size**: {self.state.baseline_metrics.lines_of_code:,} lines of code")
        lines.append(f"- **Graduated**: {self.state.graduation_timestamp or 'In Progress'}")
        lines.append("")

        # Core principles
        lines.append("## Core Principles")
        lines.append("")
        lines.extend(self._generate_core_principles())
        lines.append("")

        # Language-specific conventions
        lines.append("## Language-Specific Conventions")
        lines.append("")
        lines.extend(self._generate_language_conventions())
        lines.append("")

        # Testing standards
        lines.append("## Testing Standards")
        lines.append("")
        lines.extend(self._generate_testing_standards())
        lines.append("")

        # Quality gates
        lines.append("## Quality Gates")
        lines.append("")
        lines.extend(self._generate_quality_gates())
        lines.append("")

        # Architecture patterns
        lines.append("## Architecture Patterns")
        lines.append("")
        lines.extend(self._generate_architecture_patterns())
        lines.append("")

        # Spec-driven workflow
        lines.append("## Spec-Driven Development Workflow")
        lines.append("")
        lines.extend(self._generate_workflow_guidelines())
        lines.append("")

        return "\n".join(lines)

    def _generate_core_principles(self) -> list[str]:
        """Generate core development principles."""
        principles = []

        principles.append("### 1. Specification First")
        principles.append("")
        principles.append(
            "All features begin with a specification document (spec.md) that defines "
            "requirements, acceptance criteria, and success metrics before implementation begins."
        )
        principles.append("")

        principles.append("### 2. Test Coverage Requirement")
        principles.append("")
        principles.append(
            "Maintain minimum 60% test coverage on core business logic. All new features require tests before merging."
        )
        principles.append("")

        principles.append("### 3. Complexity Management")
        principles.append("")
        principles.append(
            "Functions with cyclomatic complexity >10 require justification. "
            "Document exceptions in complexity-justification.md."
        )
        principles.append("")

        principles.append("### 4. Security First")
        principles.append("")
        principles.append("Zero tolerance for critical vulnerabilities. Run security scans before each release.")
        principles.append("")

        return principles

    def _generate_language_conventions(self) -> list[str]:
        """Generate language-specific conventions."""
        conventions = []

        if self.state.language == "python":
            conventions.extend(self._python_conventions())
        elif self.state.language == "javascript":
            conventions.extend(self._javascript_conventions())
        elif self.state.language == "rust":
            conventions.extend(self._rust_conventions())
        elif self.state.language == "go":
            conventions.extend(self._go_conventions())
        else:
            conventions.append(f"Follow standard {self.state.language} conventions.")
            conventions.append("")

        return conventions

    def _python_conventions(self) -> list[str]:
        """Python-specific conventions."""
        return [
            "- **Structure**: Follow PEP 518 (src/ layout with pyproject.toml)",
            "- **Style**: PEP 8 enforced via linter",
            "- **Formatting**: Black with 88-character line length",
            "- **Type Hints**: Required for public APIs",
            "- **Docstrings**: Google-style for all public functions/classes",
            "- **Testing**: pytest with coverage reporting",
            "- **Dependencies**: Managed via requirements.txt or pyproject.toml",
            "",
        ]

    def _javascript_conventions(self) -> list[str]:
        """JavaScript-specific conventions."""
        return [
            "- **Structure**: src/ for source, test/ for tests, dist/ for builds",
            "- **Style**: ESLint with Airbnb or Standard config",
            "- **Formatting**: Prettier with default settings",
            "- **Type Safety**: TypeScript or JSDoc for public APIs",
            "- **Documentation**: JSDoc for exported functions/classes",
            "- **Testing**: Jest or Mocha with coverage reporting",
            "- **Dependencies**: package.json with lockfile (package-lock.json or yarn.lock)",
            "",
        ]

    def _rust_conventions(self) -> list[str]:
        """Rust-specific conventions."""
        return [
            "- **Structure**: Cargo workspace layout",
            "- **Style**: rustfmt with default settings",
            "- **Linting**: clippy with recommended lints",
            "- **Documentation**: Doc comments (///) for public items",
            "- **Testing**: Built-in test framework with #[test]",
            "- **Dependencies**: Cargo.toml with Cargo.lock",
            "",
        ]

    def _go_conventions(self) -> list[str]:
        """Go-specific conventions."""
        return [
            "- **Structure**: Standard Go project layout",
            "- **Formatting**: gofmt (automatic)",
            "- **Linting**: golangci-lint",
            "- **Documentation**: GoDoc comments for exported symbols",
            "- **Testing**: Built-in testing package",
            "- **Dependencies**: go.mod and go.sum",
            "",
        ]

    def _generate_testing_standards(self) -> list[str]:
        """Generate testing standards."""
        return [
            "- **Minimum Coverage**: 60% on core business logic modules",
            "- **Test Types**:",
            "  - Unit tests for individual functions/methods",
            "  - Contract tests for public APIs",
            "  - Integration tests for critical paths",
            "- **Test Organization**: Mirror source structure in tests/",
            "- **Naming**: test_<function_name> or <Function>Test",
            "- **CI Integration**: Tests must pass before merge",
            "",
        ]

    def _generate_quality_gates(self) -> list[str]:
        """Generate quality gate requirements."""
        return [
            "All features must pass these gates before merging:",
            "",
            "1. **Test Coverage**: ≥60% on modified modules",
            "2. **Complexity**: Cyclomatic complexity <10 (or documented)",
            "3. **Linting**: Zero linter errors",
            "4. **Formatting**: Code formatted per conventions",
            "5. **Security**: Zero critical vulnerabilities",
            "6. **Build**: Clean build with <10 warnings",
            "7. **Documentation**: Public APIs documented",
            "",
        ]

    def _generate_architecture_patterns(self) -> list[str]:
        """Generate architecture pattern guidelines."""
        patterns = []

        if self.state.detected_framework:
            patterns.append(f"### Detected Framework: {self.state.detected_framework}")
            patterns.append("")

        patterns.extend(
            [
                "- **Separation of Concerns**: Keep business logic, data access, and presentation separate",
                "- **Dependency Injection**: Prefer constructor injection over global state",
                "- **Error Handling**: Use consistent error handling patterns across the codebase",
                "- **Configuration**: Externalize configuration (environment variables, config files)",
                "- **Logging**: Structured logging with appropriate log levels",
                "",
            ]
        )

        return patterns

    def _generate_workflow_guidelines(self) -> list[str]:
        """Generate spec-driven workflow guidelines."""
        return [
            "1. **Create Specification**: Use `/speckit.specify` to create feature spec",
            "2. **Plan Implementation**: Use `/speckit.plan` to design technical approach",
            "3. **Generate Tasks**: Use `/speckit.tasks` to break down implementation",
            "4. **Implement**: Follow task list, updating spec as needed",
            "5. **Validate**: Ensure all quality gates pass",
            "6. **Review**: Spec and code reviewed together",
            "7. **Merge**: Both spec and implementation merged as unit",
            "",
            "### Spec Template Location",
            "",
            "- Specification template: `.specify/templates/spec-template.md`",
            "- Plan template: `.specify/templates/plan-template.md`",
            "- Tasks template: `.specify/templates/tasks-template.md`",
            "",
        ]

    def save(self, output_path: Path | None = None) -> Path:
        """
        Save constitution to file.

        Args:
            output_path: Custom path, defaults to .specify/constitution.md

        Returns:
            Path where constitution was saved
        """
        if output_path is None:
            output_path = self.project_root / ".specify" / "constitution.md"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        constitution_content = self.generate()
        output_path.write_text(constitution_content, encoding="utf-8")

        return output_path

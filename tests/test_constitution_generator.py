"""Unit tests for Constitution Generator (Phase 2)."""

import pytest

from brownfield.integration.speckit import ConstitutionGenerator
from brownfield.models.assessment import Metrics
from brownfield.models.state import BrownfieldState


class TestConstitutionGenerator:
    """Test ConstitutionGenerator class."""

    def test_init_with_default_template_dir(self):
        """Test initialization uses package templates directory by default."""
        generator = ConstitutionGenerator()

        assert generator.template_dir.exists()
        assert generator.template_dir.name == "templates"
        assert (generator.template_dir / "constitution.yaml.j2").exists()

    def test_init_with_custom_template_dir(self, tmp_path):
        """Test initialization with custom template directory."""
        custom_dir = tmp_path / "custom_templates"
        custom_dir.mkdir()

        generator = ConstitutionGenerator(template_dir=custom_dir)

        assert generator.template_dir == custom_dir

    def test_generate_requires_metrics(self, tmp_path):
        """Test generate() raises error if state has no metrics."""
        generator = ConstitutionGenerator()
        state = BrownfieldState()
        output_path = tmp_path / "constitution.md"

        with pytest.raises(ValueError, match="must have current_metrics"):
            generator.generate(state, output_path)

    def test_generate_creates_constitution_file(self, tmp_path):
        """Test generate() creates constitution.md file."""
        generator = ConstitutionGenerator()

        # Create state with metrics
        state = BrownfieldState()
        state.project_root = tmp_path
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.baseline_metrics = state.current_metrics

        output_path = tmp_path / "constitution.md"
        generator.generate(state, output_path)

        # Verify file created
        assert output_path.exists()
        assert output_path.is_file()

    def test_generated_constitution_content(self, tmp_path):
        """Test generated constitution contains expected sections."""
        generator = ConstitutionGenerator()

        state = BrownfieldState()
        state.project_root = tmp_path
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.baseline_metrics = state.current_metrics

        output_path = tmp_path / "constitution.md"
        generator.generate(state, output_path)

        content = output_path.read_text()

        # Check for required sections
        assert "# Project Constitution" in content
        assert "## Code Quality Standards" in content
        assert "### Complexity" in content
        assert "### Test Coverage" in content
        assert "## Testing Standards" in content
        assert "## Documentation Standards" in content
        assert "## Security Standards" in content
        assert "## Build and CI Standards" in content
        assert "## Regression Detection Thresholds" in content
        assert "## Monitoring and Maintenance" in content
        assert "## BrownKit Graduation Metadata" in content
        assert "## Spec-Kit Integration" in content

    def test_constitution_includes_metrics(self, tmp_path):
        """Test constitution includes actual metrics values."""
        generator = ConstitutionGenerator()

        state = BrownfieldState()
        state.project_root = tmp_path
        state.current_metrics = Metrics(
            test_coverage=0.75,  # 75%
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.baseline_metrics = state.current_metrics

        output_path = tmp_path / "constitution.md"
        generator.generate(state, output_path)

        content = output_path.read_text()

        # Check metrics appear in content
        assert "75" in content  # Coverage percentage
        assert "12.5" in content  # Avg complexity
        assert "45" in content  # Max complexity
        assert "15,000" in content or "15000" in content  # Total LOC
        assert "3,500" in content or "3500" in content  # Test LOC

    def test_constitution_language_detection_python(self, tmp_path):
        """Test language detection for Python projects."""
        generator = ConstitutionGenerator()

        # Create pyproject.toml to indicate Python project
        (tmp_path / "pyproject.toml").write_text("[tool.poetry]\nname = 'test'")

        state = BrownfieldState()
        state.project_root = tmp_path
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.baseline_metrics = state.current_metrics

        output_path = tmp_path / "constitution.md"
        generator.generate(state, output_path)

        content = output_path.read_text()

        # Check Python-specific content
        assert "Python" in content or "python" in content
        assert "Pytest" in content or "pytest" in content

    def test_constitution_creates_parent_directories(self, tmp_path):
        """Test generate() creates parent directories if they don't exist."""
        generator = ConstitutionGenerator()

        state = BrownfieldState()
        state.project_root = tmp_path
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        state.baseline_metrics = state.current_metrics

        # Use nested path that doesn't exist
        output_path = tmp_path / "nested" / "dir" / "constitution.md"
        generator.generate(state, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()


class TestBuildContext:
    """Test _build_context() method."""

    def test_build_context_with_baseline(self, tmp_path):
        """Test context includes baseline metrics."""
        generator = ConstitutionGenerator()

        state = BrownfieldState()
        state.project_root = tmp_path
        state.current_metrics = Metrics(
            test_coverage=0.80,
            complexity_avg=15.0,
            complexity_max=50,
            critical_vulnerabilities=0,
            high_vulnerabilities=1,
            medium_vulnerabilities=3,
            build_status="passing",
            documentation_coverage=0.70,
            total_loc=20000,
            test_loc=5000,
            git_commits=150,
            git_secrets_found=0,
        )
        state.baseline_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )

        context = generator._build_context(state)

        # Baseline metrics should be used for minimum standards
        assert context["min_coverage"] == 75  # From baseline
        assert context["baseline_coverage"] == 75.0
        assert context["baseline_complexity"] == 12.5

    def test_build_context_without_baseline_uses_current(self, tmp_path):
        """Test context uses current metrics if no baseline."""
        generator = ConstitutionGenerator()

        state = BrownfieldState()
        state.project_root = tmp_path
        state.current_metrics = Metrics(
            test_coverage=0.75,
            complexity_avg=12.5,
            complexity_max=45,
            critical_vulnerabilities=0,
            high_vulnerabilities=2,
            medium_vulnerabilities=5,
            build_status="passing",
            documentation_coverage=0.65,
            total_loc=15000,
            test_loc=3500,
            git_commits=125,
            git_secrets_found=0,
        )
        # No baseline_metrics set

        context = generator._build_context(state)

        # Should use current metrics as baseline
        assert context["baseline_coverage"] == 75.0
        assert context["baseline_complexity"] == 12.5


class TestLanguageDetection:
    """Test _detect_language() method."""

    def test_detect_python(self, tmp_path):
        """Test Python detection via pyproject.toml."""
        generator = ConstitutionGenerator()
        (tmp_path / "pyproject.toml").write_text("")

        state = BrownfieldState()
        state.project_root = tmp_path

        language = generator._detect_language(state)
        assert language == "python"

    def test_detect_javascript(self, tmp_path):
        """Test JavaScript detection via package.json."""
        generator = ConstitutionGenerator()
        (tmp_path / "package.json").write_text("{}")

        state = BrownfieldState()
        state.project_root = tmp_path

        language = generator._detect_language(state)
        assert language == "javascript"

    def test_detect_rust(self, tmp_path):
        """Test Rust detection via Cargo.toml."""
        generator = ConstitutionGenerator()
        (tmp_path / "Cargo.toml").write_text("")

        state = BrownfieldState()
        state.project_root = tmp_path

        language = generator._detect_language(state)
        assert language == "rust"

    def test_detect_go(self, tmp_path):
        """Test Go detection via go.mod."""
        generator = ConstitutionGenerator()
        (tmp_path / "go.mod").write_text("")

        state = BrownfieldState()
        state.project_root = tmp_path

        language = generator._detect_language(state)
        assert language == "go"

    def test_detect_unknown(self, tmp_path):
        """Test unknown language when no markers found."""
        generator = ConstitutionGenerator()

        state = BrownfieldState()
        state.project_root = tmp_path

        language = generator._detect_language(state)
        assert language == "unknown"

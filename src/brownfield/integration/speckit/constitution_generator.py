"""Constitution generator for Spec-Kit integration."""

from datetime import datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from brownfield.models.state import BrownfieldState


class ConstitutionGenerator:
    """Generates constitution.md for Spec-Kit from graduation metrics."""

    def __init__(self, template_dir: Path | None = None):
        """Initialize constitution generator.

        Args:
            template_dir: Directory containing constitution template
                         (defaults to package templates directory)
        """
        if template_dir is None:
            # Default to package templates directory
            template_dir = Path(__file__).parent / "templates"

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(enabled_extensions=()),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self, state: BrownfieldState, output_path: Path) -> None:
        """Generate constitution.md from state metrics.

        Args:
            state: BrownfieldState with graduation metrics
            output_path: Path to write constitution.md

        Raises:
            ValueError: If state doesn't have required metrics
        """
        if not state.current_metrics:
            raise ValueError("State must have current_metrics to generate constitution")

        # Prepare template context
        context = self._build_context(state)

        # Render YAML template
        template = self.env.get_template("constitution.yaml.j2")
        yaml_content = template.render(**context)

        # Parse YAML to dict
        constitution_data = yaml.safe_load(yaml_content)

        # Convert to markdown
        markdown = self._yaml_to_markdown(constitution_data)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")

    def _build_context(self, state: BrownfieldState) -> dict:
        """Build template context from state.

        Args:
            state: BrownfieldState with metrics

        Returns:
            Dictionary of template variables
        """
        metrics = state.current_metrics
        baseline = state.baseline_metrics or metrics

        return {
            # Project metadata
            "project_name": state.project_root.name if state.project_root else "Unknown",
            "language": self._detect_language(state),
            "graduation_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "graduation_timestamp": datetime.utcnow().isoformat(),
            "brownkit_version": state.ai_agent_version,
            # Complexity standards
            "max_complexity": metrics.complexity_max,
            "avg_complexity": round(metrics.complexity_avg, 1),
            # Coverage standards (use baseline as minimum)
            "min_coverage": max(60, int(baseline.test_coverage * 100)),
            "target_coverage": max(70, int(metrics.test_coverage * 100) + 5),
            "baseline_coverage": round(baseline.test_coverage * 100, 1),
            # Vulnerability limits
            "max_high_vulns": max(2, metrics.high_vulnerabilities),
            # Documentation
            "min_doc_coverage": int(metrics.documentation_coverage * 100),
            # Code metrics
            "total_loc": metrics.total_loc,
            "test_loc": metrics.test_loc,
            "baseline_complexity": round(baseline.complexity_avg, 1),
            "baseline_max_complexity": baseline.complexity_max,
            # Regression thresholds
            "coverage_drop_threshold": 5.0,  # 5 percentage points
            "complexity_increase_threshold": 20.0,  # 20% increase
            # Monitoring
            "monitoring_frequency": "Weekly",
        }

    def _detect_language(self, state: BrownfieldState) -> str:
        """Detect project language from state or directory.

        Args:
            state: BrownfieldState

        Returns:
            Language name (python, javascript, rust, go, or unknown)
        """
        # This is a simplified detection - you might want to enhance it
        if state.project_root:
            if (state.project_root / "pyproject.toml").exists():
                return "python"
            if (state.project_root / "package.json").exists():
                return "javascript"
            if (state.project_root / "Cargo.toml").exists():
                return "rust"
            if (state.project_root / "go.mod").exists():
                return "go"

        return "unknown"

    def _yaml_to_markdown(self, data: dict) -> str:
        """Convert constitution YAML data to formatted markdown.

        Args:
            data: Constitution data dictionary

        Returns:
            Formatted markdown string
        """
        lines = []

        # Header
        lines.append(f"# Project Constitution: {data.get('project_name', 'Unknown')}")
        lines.append("")
        lines.append(
            f"**Language**: {data.get('language', 'unknown').capitalize()} | "
            f"**Graduated**: {data.get('graduation_date', 'Unknown')} | "
            f"**BrownKit**: v{data.get('brownkit_version', '0.0.0')}"
        )
        lines.append("")
        lines.append(
            "This constitution defines the quality standards and requirements "
            "for this project after graduating from BrownKit's brownfield workflow. "
            "All future development must maintain or improve these standards."
        )
        lines.append("")

        # Quality Standards
        lines.append("## Code Quality Standards")
        lines.append("")
        quality = data.get("quality_standards", {})

        if "complexity" in quality:
            comp = quality["complexity"]
            lines.append("### Complexity")
            lines.append(f"- **Maximum Cyclomatic Complexity**: {comp['max_cyclomatic_complexity']}")
            lines.append(f"- **Target Average Complexity**: {comp['average_complexity_target']}")
            lines.append(f"- {comp['description']}")
            lines.append("")

        if "test_coverage" in quality:
            cov = quality["test_coverage"]
            lines.append("### Test Coverage")
            lines.append(f"- **Minimum Coverage**: {cov['minimum_coverage']}%")
            lines.append(f"- **Target Coverage**: {cov['target_coverage']}%")
            lines.append(f"- {cov['description']}")
            lines.append("")

        if "code_quality" in quality:
            qual = quality["code_quality"]
            lines.append("### Code Quality")
            lines.append(f"- **Critical Vulnerabilities**: {qual['critical_vulnerabilities']} (zero tolerance)")
            lines.append(f"- **Max High Vulnerabilities**: {qual['high_vulnerabilities_max']}")
            lines.append(f"- **Build Status**: {qual['build_status']}")
            lines.append(f"- {qual['description']}")
            lines.append("")

        # Testing Standards
        lines.append("## Testing Standards")
        lines.append("")
        testing = data.get("testing_standards", {})

        if "required_test_types" in testing:
            lines.append("### Required Test Types")
            for test_type in testing["required_test_types"]:
                lines.append(f"- {test_type}")
            lines.append("")

        if "test_execution" in testing:
            exec_std = testing["test_execution"]
            lines.append("### Test Execution")
            lines.append(f"- **Frequency**: {exec_std.get('frequency', 'On every commit')}")
            lines.append(f"- **CI Integration**: {exec_std.get('ci_integration', 'Required')}")
            lines.append(f"- **Failing Tests**: {exec_std.get('failing_tests', 'Block merge')}")
            lines.append("")

        # Documentation Standards
        lines.append("## Documentation Standards")
        lines.append("")
        docs = data.get("documentation_standards", {})
        lines.append(f"**Minimum Coverage**: {docs.get('minimum_coverage', 0)}%")
        lines.append("")

        if "required_sections" in docs:
            lines.append("### Required Documentation")
            for section in docs["required_sections"]:
                lines.append(f"- {section}")
            lines.append("")

        # Security Standards
        lines.append("## Security Standards")
        lines.append("")
        security = data.get("security_standards", {})

        if "vulnerability_scanning" in security:
            vuln = security["vulnerability_scanning"]
            lines.append("### Vulnerability Scanning")
            lines.append(f"- **Enabled**: {vuln.get('enabled', True)}")
            lines.append(f"- **Frequency**: {vuln.get('frequency', 'Weekly')}")
            if "tools" in vuln:
                lines.append(f"- **Tools**: {', '.join(vuln['tools'])}")
            lines.append("")

        if "secrets_management" in security:
            secrets = security["secrets_management"]
            lines.append("### Secrets Management")
            lines.append(f"- No secrets in code: {'✅' if secrets.get('no_secrets_in_code') else '❌'}")
            lines.append(f"- Environment variables: {secrets.get('environment_variables', 'Required')}")
            lines.append(f"- Secrets scanner: {secrets.get('secrets_scanner', 'Required')}")
            lines.append("")

        # Build and CI Standards
        lines.append("## Build and CI Standards")
        lines.append("")
        build = data.get("build_standards", {})

        if "continuous_integration" in build:
            ci = build["continuous_integration"]
            lines.append("### CI Pipeline")
            if "pipeline_steps" in ci:
                for step in ci["pipeline_steps"]:
                    lines.append(f"- {step}")
            lines.append("")

        # Regression Detection
        lines.append("## Regression Detection Thresholds")
        lines.append("")
        lines.append("**These thresholds trigger BrownKit workflow re-entry if violated:**")
        lines.append("")
        regression = data.get("regression_thresholds", {})
        for key, value in regression.items():
            formatted_key = key.replace("_", " ").title()
            lines.append(f"- **{formatted_key}**: {value}")
        lines.append("")

        # Monitoring
        lines.append("## Monitoring and Maintenance")
        lines.append("")
        monitoring = data.get("monitoring", {})
        lines.append(f"**Frequency**: {monitoring.get('frequency', 'Weekly')}")
        lines.append(f"**Automated Checks**: {'✅' if monitoring.get('automated_checks') else '❌'}")
        lines.append("")

        if "metrics_tracked" in monitoring:
            lines.append("### Metrics Tracked")
            for metric in monitoring["metrics_tracked"]:
                lines.append(f"- {metric}")
            lines.append("")

        # BrownKit Metadata
        lines.append("## BrownKit Graduation Metadata")
        lines.append("")
        metadata = data.get("brownkit_metadata", {})

        if "graduation_metrics" in metadata:
            grad_metrics = metadata["graduation_metrics"]
            lines.append("### Graduation Baseline Metrics")
            lines.append(f"- **Test Coverage**: {grad_metrics.get('test_coverage', 0)}%")
            lines.append(f"- **Average Complexity**: {grad_metrics.get('complexity_avg', 0)}")
            lines.append(f"- **Max Complexity**: {grad_metrics.get('complexity_max', 0)}")
            lines.append(f"- **Total LOC**: {grad_metrics.get('total_loc', 0):,}")
            lines.append(f"- **Test LOC**: {grad_metrics.get('test_loc', 0):,}")
            lines.append("")

        # Spec-Kit Integration
        lines.append("## Spec-Kit Integration")
        lines.append("")
        speckit = data.get("speckit_integration", {})

        if "next_steps" in speckit:
            lines.append("### Next Steps")
            for step in speckit["next_steps"]:
                lines.append(f"- {step}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(
            "*This constitution was automatically generated by BrownKit upon "
            f"graduation on {data.get('graduation_date', 'Unknown')}.*"
        )

        return "\n".join(lines)

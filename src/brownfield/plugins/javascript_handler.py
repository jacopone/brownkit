"""JavaScript language handler stub."""

from pathlib import Path
from typing import Optional
from brownfield.models.assessment import ConfidenceLevel
from brownfield.plugins.base import DetectionResult, LanguageHandler, QualitySetupResult, TestSetupResult
from brownfield.plugins.registry import register_handler

@register_handler("javascript")
class JavaScriptHandler(LanguageHandler):
    """JavaScript/Node.js language handler."""

    def detect(self, project_root: Path) -> Optional[DetectionResult]:
        if (project_root / "package.json").exists():
            return DetectionResult(
                language="javascript",
                confidence=ConfidenceLevel.HIGH,
                version=None,
                framework=None,
                evidence={"package.json": "Found Node.js project config"},
            )
        return None

    def get_standard_structure(self) -> dict[str, list[str]]:
        return {"src": [], "test": [], "dist": []}

    def bootstrap_tests(self, project_root: Path, core_modules: list[Path], coverage_target: float = 0.6) -> TestSetupResult:
        return TestSetupResult("jest", [], [], 0.0, 0, 0)

    def install_quality_gates(self, project_root: Path, complexity_threshold: int = 10) -> QualitySetupResult:
        return QualitySetupResult("eslint", "prettier", 0, 0, 0, [], 0)

    def verify_build(self, project_root: Path) -> bool:
        return True

    def measure_complexity(self, project_root: Path) -> dict[str, float]:
        """Use lizard for complexity analysis on JavaScript files."""
        import xml.etree.ElementTree as ET
        from brownfield.orchestrator.process_runner import ProcessRunner

        try:
            # Run lizard with XML output for JavaScript files
            result = ProcessRunner.run(
                ["lizard", str(project_root), "--xml", "-l", "javascript"],
                cwd=str(project_root),
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0 and not result.stdout:
                # Lizard failed completely, return safe defaults
                return {"average": 0.0, "maximum": 0.0, "violations": 0.0}

            # Parse lizard XML output
            root = ET.fromstring(result.stdout)

            # Extract complexity metrics
            complexities = []
            violations = 0

            for measure in root.findall(".//measure[@type='Function']"):
                for item in measure.findall("item"):
                    values = item.findall("value")
                    if len(values) >= 3:
                        try:
                            ccn = int(values[2].text)  # CCN is the 3rd value
                            complexities.append(ccn)
                            if ccn > 10:
                                violations += 1
                        except (ValueError, AttributeError):
                            continue

            if not complexities:
                return {"average": 0.0, "maximum": 0.0, "violations": 0.0}

            return {
                "average": sum(complexities) / len(complexities),
                "maximum": float(max(complexities)),
                "violations": float(violations),
            }

        except (ET.ParseError, ValueError):
            # Tool not available or failed
            return {"average": 0.0, "maximum": 0.0, "violations": 0.0}

    def scan_security(self, project_root: Path) -> dict[str, int]:
        """Run npm audit security scanner."""
        import json
        from brownfield.orchestrator.process_runner import ProcessRunner

        try:
            # Run npm audit with JSON output
            result = ProcessRunner.run(
                ["npm", "audit", "--json"],
                cwd=str(project_root),
                timeout=300,  # 5 minute timeout
            )

            # npm audit returns non-zero when vulnerabilities found
            if not result.stdout:
                return {"critical": 0, "high": 0, "medium": 0, "low": 0}

            # Parse npm audit JSON output
            data = json.loads(result.stdout)

            # Count vulnerabilities by severity
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

            # npm audit v7+ format
            if "vulnerabilities" in data:
                vuln_data = data["vulnerabilities"]
                for severity in ["critical", "high", "medium", "low"]:
                    severity_counts[severity] = vuln_data.get(severity, 0)
            # npm audit v6 format
            elif "metadata" in data and "vulnerabilities" in data["metadata"]:
                vuln_data = data["metadata"]["vulnerabilities"]
                for severity in ["critical", "high", "medium", "low"]:
                    severity_counts[severity] = vuln_data.get(severity, 0)

            return severity_counts

        except (json.JSONDecodeError, ValueError, KeyError):
            # Tool not available or failed
            return {"critical": 0, "high": 0, "medium": 0, "low": 0}

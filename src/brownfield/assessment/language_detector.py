"""Language detection engine."""

from pathlib import Path

from brownfield.models.assessment import ConfidenceLevel, LanguageDetection
from brownfield.plugins.registry import list_supported_languages, get_handler


class LanguageDetector:
    """Detects primary and secondary languages in project."""

    def detect(self, project_root: Path) -> LanguageDetection:
        """
        Detect primary language with confidence level.

        Args:
            project_root: Path to project directory

        Returns:
            LanguageDetection with primary language and confidence

        Raises:
            RuntimeError: If no language detected
        """
        detections = []

        # Try all registered language handlers
        for lang in list_supported_languages():
            try:
                handler = get_handler(lang)
                result = handler.detect(project_root)
                if result:
                    detections.append((result, result.confidence.value))
            except Exception:
                continue

        if not detections:
            raise RuntimeError(
                f"Could not detect primary language in {project_root}. "
                "Use --language to specify manually."
            )

        # Sort by confidence
        detections.sort(key=lambda x: x[1], reverse=True)
        primary = detections[0][0]

        # Collect secondary languages
        secondary_languages = [
            (det.language, det.confidence.value)
            for det, _ in detections[1:]
            if det.confidence.value >= ConfidenceLevel.MEDIUM.value
        ]

        return LanguageDetection(
            language=primary.language,
            confidence=primary.confidence,
            version=primary.version,
            framework=primary.framework,
            secondary_languages=secondary_languages,
            detection_evidence=primary.evidence,
        )

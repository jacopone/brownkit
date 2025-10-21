"""Plugin system for language-specific handlers."""

from brownfield.plugins.base import (
    DetectionResult,
    LanguageHandler,
    QualitySetupResult,
    StructureResult,
    TestSetupResult,
)
from brownfield.plugins.registry import get_handler, list_supported_languages, register_handler

# Import handlers to trigger registration
from brownfield.plugins import go_handler as _go_handler
from brownfield.plugins import javascript_handler as _javascript_handler
from brownfield.plugins import python_handler as _python_handler
from brownfield.plugins import rust_handler as _rust_handler

# Keep references to prevent garbage collection
_ = (_go_handler, _javascript_handler, _python_handler, _rust_handler)

__all__ = [
    "DetectionResult",
    "LanguageHandler",
    "QualitySetupResult",
    "StructureResult",
    "TestSetupResult",
    "get_handler",
    "list_supported_languages",
    "register_handler",
]

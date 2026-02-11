"""Contract tests for plugin interface compliance.

Verifies that all language handlers implement the LanguageHandler interface correctly.
"""

import inspect
from pathlib import Path

import pytest

from brownfield.plugins.base import LanguageHandler
from brownfield.plugins.go_handler import GoHandler
from brownfield.plugins.javascript_handler import JavaScriptHandler
from brownfield.plugins.python_handler import PythonHandler
from brownfield.plugins.rust_handler import RustHandler

# All plugin classes to test
PLUGIN_CLASSES = [
    PythonHandler,
    JavaScriptHandler,
    RustHandler,
    GoHandler,
]


class TestPluginInterfaceCompliance:
    """Test that all plugins implement the required interface."""

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_inherits_from_language_handler(self, plugin_class):
        """Plugin must inherit from LanguageHandler."""
        assert issubclass(plugin_class, LanguageHandler), f"{plugin_class.__name__} must inherit from LanguageHandler"

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_has_detect_method(self, plugin_class):
        """Plugin must implement detect() method."""
        assert hasattr(plugin_class, "detect"), f"{plugin_class.__name__} must implement detect() method"

        # Check method signature
        method = plugin_class.detect
        sig = inspect.signature(method)

        # Should have 'self' and 'project_root' parameters
        params = list(sig.parameters.keys())
        assert "project_root" in params, f"{plugin_class.__name__}.detect() must have 'project_root' parameter"

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_has_get_standard_structure_method(self, plugin_class):
        """Plugin must implement get_standard_structure() method."""
        assert hasattr(plugin_class, "get_standard_structure"), (
            f"{plugin_class.__name__} must implement get_standard_structure() method"
        )

        # Verify return type annotation if present
        method = plugin_class.get_standard_structure
        sig = inspect.signature(method)

        # Should return dict
        if sig.return_annotation != inspect.Signature.empty:
            assert "dict" in str(sig.return_annotation), (
                f"{plugin_class.__name__}.get_standard_structure() should return dict"
            )

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_has_bootstrap_tests_method(self, plugin_class):
        """Plugin must implement bootstrap_tests() method."""
        assert hasattr(plugin_class, "bootstrap_tests"), (
            f"{plugin_class.__name__} must implement bootstrap_tests() method"
        )

        method = plugin_class.bootstrap_tests
        sig = inspect.signature(method)

        # Should have 'project_root' parameter
        params = list(sig.parameters.keys())
        assert "project_root" in params, f"{plugin_class.__name__}.bootstrap_tests() must have 'project_root' parameter"

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_has_install_quality_gates_method(self, plugin_class):
        """Plugin must implement install_quality_gates() method."""
        assert hasattr(plugin_class, "install_quality_gates"), (
            f"{plugin_class.__name__} must implement install_quality_gates() method"
        )

        method = plugin_class.install_quality_gates
        sig = inspect.signature(method)

        # Should have 'project_root' parameter
        params = list(sig.parameters.keys())
        assert "project_root" in params, (
            f"{plugin_class.__name__}.install_quality_gates() must have 'project_root' parameter"
        )

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_can_instantiate(self, plugin_class):
        """Plugin must be instantiable without arguments."""
        try:
            instance = plugin_class()
            assert instance is not None
        except TypeError as e:
            pytest.fail(f"{plugin_class.__name__} cannot be instantiated without arguments: {e}")

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_detect_returns_valid_result(self, plugin_class, tmp_path):
        """Plugin detect() must return None or LanguageDetection."""
        instance = plugin_class()
        result = instance.detect(tmp_path)

        # Result must be None (not detected) or have required attributes
        if result is not None:
            assert hasattr(result, "language"), (
                f"{plugin_class.__name__}.detect() result must have 'language' attribute"
            )
            assert hasattr(result, "confidence"), (
                f"{plugin_class.__name__}.detect() result must have 'confidence' attribute"
            )

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_get_standard_structure_returns_dict(self, plugin_class):
        """Plugin get_standard_structure() must return a dictionary."""
        instance = plugin_class()
        structure = instance.get_standard_structure()

        assert isinstance(structure, dict), f"{plugin_class.__name__}.get_standard_structure() must return a dict"

        # Verify structure has expected keys
        for key, value in structure.items():
            assert isinstance(key, str), f"{plugin_class.__name__}.get_standard_structure() keys must be strings"
            assert isinstance(value, list), f"{plugin_class.__name__}.get_standard_structure() values must be lists"


class TestPluginDetection:
    """Test plugin detection capabilities on fixture projects."""

    def _fixture_has_content(self, fixture_path: Path) -> bool:
        """Check if fixture directory has actual content (not just an empty submodule)."""
        if not fixture_path.exists():
            return False
        return any(fixture_path.iterdir())

    def test_python_handler_detects_python_fixture(self):
        """PythonHandler should detect Python fixture project."""
        handler = PythonHandler()
        fixture_path = Path(__file__).parent.parent / "fixtures" / "python_messy"

        if not self._fixture_has_content(fixture_path):
            pytest.skip("Fixture submodule not initialized")
        result = handler.detect(fixture_path)
        assert result is not None, "PythonHandler should detect Python fixture"
        assert result.language == "python"

    def test_javascript_handler_detects_javascript_fixture(self):
        """JavaScriptHandler should detect JavaScript fixture project."""
        handler = JavaScriptHandler()
        fixture_path = Path(__file__).parent.parent / "fixtures" / "javascript_unstructured"

        if not self._fixture_has_content(fixture_path):
            pytest.skip("Fixture submodule not initialized")
        result = handler.detect(fixture_path)
        assert result is not None, "JavaScriptHandler should detect JavaScript fixture"
        assert result.language == "javascript"

    def test_rust_handler_detects_rust_fixture(self):
        """RustHandler should detect Rust fixture project."""
        handler = RustHandler()
        fixture_path = Path(__file__).parent.parent / "fixtures" / "rust_complex"

        if not self._fixture_has_content(fixture_path):
            pytest.skip("Fixture submodule not initialized")
        result = handler.detect(fixture_path)
        assert result is not None, "RustHandler should detect Rust fixture"
        assert result.language == "rust"

    def test_go_handler_detects_go_fixture(self):
        """GoHandler should detect Go fixture project."""
        handler = GoHandler()
        fixture_path = Path(__file__).parent.parent / "fixtures" / "go_unorganized"

        if not self._fixture_has_content(fixture_path):
            pytest.skip("Fixture submodule not initialized")
        result = handler.detect(fixture_path)
        assert result is not None, "GoHandler should detect Go fixture"
        assert result.language == "go"

    def test_handlers_return_none_for_wrong_language(self, tmp_path):
        """Handlers should return None for projects of other languages."""
        # Create a Python-specific file
        python_file = tmp_path / "requirements.txt"
        python_file.write_text("requests==2.28.0\n")

        # Non-Python handlers should return None
        js_handler = JavaScriptHandler()
        assert js_handler.detect(tmp_path) is None, "JS handler should not detect Python project"

        rust_handler = RustHandler()
        assert rust_handler.detect(tmp_path) is None, "Rust handler should not detect Python project"

        go_handler = GoHandler()
        assert go_handler.detect(tmp_path) is None, "Go handler should not detect Python project"


class TestPluginStandardStructures:
    """Test that plugins define sensible standard structures."""

    @pytest.mark.parametrize("plugin_class", PLUGIN_CLASSES)
    def test_standard_structure_has_src_or_lib(self, plugin_class):
        """Standard structure should include source directory."""
        instance = plugin_class()
        structure = instance.get_standard_structure()

        # Should have at least one of: src, lib, or language-specific convention
        keys = structure.keys()
        src_like_keys = [k for k in keys if k in ("src", "lib", "pkg", "cmd")]

        assert len(src_like_keys) > 0, f"{plugin_class.__name__} standard structure should include source directory"

    @pytest.mark.parametrize("plugin_class", [c for c in PLUGIN_CLASSES if c != GoHandler])
    def test_standard_structure_has_tests(self, plugin_class):
        """Standard structure should include test directory (Go excluded: tests live alongside code)."""
        instance = plugin_class()
        structure = instance.get_standard_structure()

        keys = structure.keys()
        test_like_keys = [k for k in keys if "test" in k.lower()]

        assert len(test_like_keys) > 0, f"{plugin_class.__name__} standard structure should include test directory"

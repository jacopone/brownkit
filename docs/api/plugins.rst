Plugins Module
==============

The plugins module provides language-specific handlers for brownfield transformation.

.. currentmodule:: brownfield.plugins

Base Handler
------------

.. automodule:: brownfield.plugins.base
   :members:
   :undoc-members:
   :show-inheritance:

Language Handlers
-----------------

Python Handler
~~~~~~~~~~~~~~

.. automodule:: brownfield.plugins.python_handler
   :members:
   :undoc-members:
   :show-inheritance:

JavaScript Handler
~~~~~~~~~~~~~~~~~~

.. automodule:: brownfield.plugins.javascript_handler
   :members:
   :undoc-members:
   :show-inheritance:

Rust Handler
~~~~~~~~~~~~

.. automodule:: brownfield.plugins.rust_handler
   :members:
   :undoc-members:
   :show-inheritance:

Go Handler
~~~~~~~~~~

.. automodule:: brownfield.plugins.go_handler
   :members:
   :undoc-members:
   :show-inheritance:

Plugin Registry
---------------

.. automodule:: brownfield.plugins.registry
   :members:
   :undoc-members:
   :show-inheritance:

Creating Custom Plugins
-----------------------

To create a custom language plugin:

1. **Implement LanguageHandler Interface**

   .. code-block:: python

      from brownfield.plugins.base import LanguageHandler
      from pathlib import Path
      from typing import Optional

      class MyLanguageHandler(LanguageHandler):
          def detect(self, project_root: Path) -> Optional[DetectionResult]:
              # Detection logic
              pass

          def bootstrap_tests(self, project_root, core_modules, coverage_target):
              # Test setup logic
              pass

          def install_linters(self, project_root):
              # Linter installation logic
              pass

          def install_formatters(self, project_root):
              # Formatter installation logic
              pass

2. **Register Plugin**

   .. code-block:: python

      from brownfield.plugins.registry import register_plugin

      register_plugin('mylanguage', MyLanguageHandler)

3. **Test Plugin**

   Create contract tests to verify interface compliance:

   .. code-block:: python

      import pytest
      from brownfield.plugins.base import LanguageHandler

      def test_plugin_interface_compliance():
          handler = MyLanguageHandler()
          assert isinstance(handler, LanguageHandler)
          assert hasattr(handler, 'detect')
          assert hasattr(handler, 'bootstrap_tests')

Examples
--------

**Detecting a Python Project:**

.. code-block:: python

    from brownfield.plugins.python_handler import PythonHandler
    from pathlib import Path

    handler = PythonHandler()
    result = handler.detect(Path("/path/to/project"))

    if result:
        print(f"Language: {result.language}")
        print(f"Confidence: {result.confidence}")
        print(f"Framework: {result.framework}")

**Bootstrapping Tests:**

.. code-block:: python

    from brownfield.plugins.python_handler import PythonHandler
    from pathlib import Path

    handler = PythonHandler()
    result = handler.bootstrap_tests(
        project_root=Path("/path/to/project"),
        core_modules=[Path("src/core.py")],
        coverage_target=0.7
    )

    print(f"Framework: {result.framework}")
    print(f"Coverage: {result.coverage}")
    print(f"Tests generated: {result.tests_generated}")

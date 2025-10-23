API Reference
=============

This section provides detailed API documentation for all BrownKit modules.

Core Modules
------------

.. toctree::
   :maxdepth: 2

   plugins
   orchestrator
   models
   cli
   assessment
   remediation
   state

Overview
--------

BrownKit's architecture consists of several key layers:

**Plugin Layer** - Language-specific handlers (Python, JavaScript, Rust, Go)
   Extensible plugin architecture for adding new language support.

**Orchestrator Layer** - Workflow orchestration and state management
   Manages phase transitions, checkpoints, and workflow coordination.

**Models Layer** - Data structures and types
   Core data models for state, assessment, checkpoints, and gates.

**CLI Layer** - Command-line interface
   User-facing commands for brownfield transformation workflow.

**Assessment Layer** - Codebase analysis
   Language detection, metrics collection, tech debt analysis.

**Remediation Layer** - Code transformation
   Structure, testing, and quality remediation workflows.

**State Layer** - Persistence and checkpoints
   JSON-based state management with Spec-Kit compatibility.

Public API Surface
------------------

The following modules constitute BrownKit's stable public API:

**Stable APIs** (safe to use in extensions):

* :py:mod:`brownfield.plugins.base` - ``LanguageHandler`` interface
* :py:mod:`brownfield.models.state` - State models (``Phase``, ``BrownfieldState``)
* :py:mod:`brownfield.models.assessment` - Assessment models (``Metrics``, ``DetectionResult``)
* :py:mod:`brownfield.models.gate` - Readiness gates (``Gate``, ``GateResult``)
* :py:mod:`brownfield.exceptions` - Custom exceptions

**Internal APIs** (subject to change):

* Orchestrator internals
* CLI implementation details
* Utility modules

Plugin Development
------------------

To create a custom language plugin, implement the :py:class:`~brownfield.plugins.base.LanguageHandler` interface:

.. code-block:: python

    from brownfield.plugins.base import LanguageHandler, DetectionResult
    from pathlib import Path
    from typing import Optional

    class TypeScriptHandler(LanguageHandler):
        def detect(self, project_root: Path) -> Optional[DetectionResult]:
            \"\"\"Detect TypeScript project.\"\"\"
            if (project_root / "tsconfig.json").exists():
                return DetectionResult(
                    language="typescript",
                    confidence=ConfidenceLevel.HIGH,
                    framework="Node.js"
                )
            return None

        def bootstrap_tests(self, project_root: Path, ...) -> TestSetupResult:
            \"\"\"Bootstrap jest test framework.\"\"\"
            # Implementation
            ...

See :doc:`plugins` for complete documentation.

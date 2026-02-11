BrownKit Documentation
======================

**BrownKit** is the official brownfield companion to Spec-Kit, transforming legacy codebases into spec-ready, production-grade projects with AI-driven automation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/index
   api/plugins
   api/orchestrator
   api/models
   api/cli
   api/assessment
   api/remediation
   api/state

Overview
--------

BrownKit automates the entire transition journey from chaotic brownfield code to clean, testable, spec-ready code through a 6-phase workflow:

1. **Assessment** - Detect language, measure metrics, identify debt
2. **Structure** - Reorganize to ecosystem standards
3. **Testing** - Bootstrap frameworks, generate tests, achieve 60%+ coverage
4. **Quality** - Install linters, formatters, pre-commit hooks
5. **Validation** - Check 7 readiness gates
6. **Graduation** - Generate Spec-Kit constitution

Quick Start
-----------

Installation::

    pip install brownkit

Basic Usage::

    # Transform your codebase
    cd /path/to/your/project
    brownfield assess
    brownfield structure
    brownfield testing
    brownfield quality
    brownfield graduate

Key Features
------------

* **Automated Assessment** - Language detection, baseline metrics, tech debt analysis
* **Structure Remediation** - Ecosystem-standard reorganization with import updates
* **Test Infrastructure** - Framework bootstrap, contract test generation, 60%+ coverage
* **Quality Gates** - Linters, formatters, complexity < 10, security scanning
* **Spec-Kit Integration** - Constitution generation, state compatibility
* **Safety First** - Atomic commits, auto-revert, Git safety layer

Supported Languages
-------------------

* **Python** - pytest, ruff, black, bandit
* **JavaScript** - jest, eslint, prettier, npm audit
* **Rust** - cargo test, clippy, rustfmt, cargo audit
* **Go** - go test, golangci-lint, gofmt, gosec

API Reference
-------------

.. toctree::
   :maxdepth: 3
   :caption: API Documentation:

   api/index

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

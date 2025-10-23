# Basic Python Transformation Example

This example demonstrates a complete brownfield transformation of a simple Python project.

## Overview

**Project**: A basic calculator application
**Issues**: Poor structure, no tests, high complexity, hardcoded values
**Goal**: Production-ready codebase with 60%+ test coverage

## Before State

```
before/
├── calc.py           # Everything in one file (150 lines)
├── config.txt        # Hardcoded configuration
└── README.txt        # Minimal documentation
```

**Problems:**
- ❌ No src/ structure
- ❌ No tests
- ❌ No linter or formatter
- ❌ High complexity (CCN > 15)
- ❌ Hardcoded configuration
- ❌ No type hints

## After State

```
after/
├── src/
│   └── calculator/
│       ├── __init__.py
│       ├── operations.py     # Basic operations (CCN < 5)
│       ├── advanced.py       # Advanced operations (CCN < 8)
│       └── config.py         # Configuration management
├── tests/
│   ├── conftest.py
│   ├── test_operations.py
│   └── test_advanced.py
├── pyproject.toml
├── .ruff.toml
├── README.md
└── .gitignore
```

**Improvements:**
- ✅ src/ layout with proper package structure
- ✅ 68% test coverage (exceeds 60% target)
- ✅ Ruff linter + formatter configured
- ✅ Complexity reduced (CCN avg: 6)
- ✅ Configuration externalized
- ✅ Type hints on all functions
- ✅ Comprehensive documentation

## Step-by-Step Walkthrough

### Step 1: Initial Assessment

```bash
cd examples/basic-python/before

# Run assessment
brownfield assess --quick

# Output:
# ✓ Language detected: Python 3.11
# ✓ Baseline metrics collected
#   - Test coverage: 0%
#   - Complexity (CCN): 18 avg
#   - Structure: Not standard
```

**Generated Files:**
- `.specify/memory/state.json` - Workflow state
- `.specify/memory/assessment-report.md` - Detailed analysis

**Key Findings:**
- No test framework detected
- Files not organized by src/ convention
- High complexity in main calculator functions
- Hardcoded configuration values

---

### Step 2: Fix Structure

```bash
brownfield structure

# Output:
# ✓ Structure analysis complete
# ✓ Generated refactoring plan
#   - Move calc.py → src/calculator/
#   - Split into operations.py + advanced.py
#   - Create __init__.py
```

**What Happened:**
- Generated human-readable refactoring plan
- Created shell scripts for file moves (not executed automatically)
- Updated import paths in moved files

**Manual Action Required:**
Review and execute the refactoring plan (human-in-the-loop by design).

---

### Step 3: Add Test Infrastructure

```bash
brownfield testing --coverage-target 0.6

# Output:
# ✓ pytest framework installed
# ✓ tests/ directory created
# ✓ conftest.py generated
# ✓ 8 test files generated
# ✓ Coverage: 68% (target: 60%)
```

**Generated Tests:**
- Unit tests for each function
- Edge case tests (division by zero, etc.)
- Integration tests for calculator workflows

---

### Step 4: Install Quality Gates

```bash
brownfield quality

# Output:
# ✓ Ruff linter installed
# ✓ Ruff formatter configured
# ✓ pyproject.toml created
# ✓ Pre-commit hooks configured
# ✓ Complexity reduced to CCN < 10
```

**Quality Improvements:**
- Linting configured (line-length: 100)
- Formatter applied to all files
- Complexity violations fixed
- Pre-commit hooks enforce quality on commits

---

### Step 5: Validate & Graduate

```bash
brownfield validate

# Output:
# ✅ Structure: src/ layout confirmed
# ✅ Testing: 68% coverage (target: 60%)
# ✅ Build: All tests passing
# ✅ Linting: Ruff checks passing
# ✅ Complexity: CCN avg 6 (threshold: 10)
# ✅ Security: No vulnerabilities found
# ✅ Documentation: README.md present
#
# 7/7 gates passed ✅

brownfield graduate

# Output:
# ✓ Constitution generated (.specify/memory/constitution.md)
# ✓ Graduation report created
# ✓ Brownfield artifacts archived
# ✓ Project ready for Spec-Kit workflow
```

---

## Comparing Before/After

### Metrics Comparison

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Test Coverage** | 0% | 68% | +68% |
| **Complexity (CCN)** | 18 avg | 6 avg | -67% |
| **Lines of Code** | 150 | 180 | +20% (tests) |
| **Files** | 3 | 12 | +9 (structure) |
| **Linting Errors** | 47 | 0 | -100% |
| **Security Issues** | 2 | 0 | -100% |

### Code Quality Comparison

**Before (calc.py):**
```python
# High complexity, no types, hardcoded values
def calculate(op, a, b):
    if op == "add":
        return a + b
    elif op == "subtract":
        return a - b
    # ... 15 more elif statements
    else:
        print("Error")  # Poor error handling
        return None
```

**After (src/calculator/operations.py):**
```python
from typing import Union

def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b
```

---

## Time Investment

- **Assessment**: 2 minutes
- **Structure refactoring**: 10 minutes (manual review + execution)
- **Test generation**: 5 minutes (automated)
- **Quality setup**: 3 minutes (automated)
- **Validation**: 1 minute
- **Total**: ~20 minutes

**ROI**: From 0% coverage, high complexity code to production-ready in 20 minutes.

---

## Key Learnings

1. **Human-in-the-loop refactoring**: BrownKit generates plans but requires manual approval for safety
2. **Incremental commits**: Each phase creates atomic Git commits for easy rollback
3. **Quality gates**: 7 readiness gates ensure consistent quality standards
4. **Spec-Kit ready**: Graduated projects are ready for spec-driven development

---

## Try It Yourself

```bash
# Copy before/ to a new directory
cp -r examples/basic-python/before /tmp/my-calculator
cd /tmp/my-calculator

# Run the brownfield workflow
brownfield assess
brownfield structure
# ... review and apply structure changes ...
brownfield testing
brownfield quality
brownfield graduate

# Compare with after/
diff -r /tmp/my-calculator ../after
```

---

## Next Steps

- Try the [CI Integration Example](../ci-integration/README.md)
- Read the [Full Documentation](https://brownkit.readthedocs.io)
- Explore the [API Reference](https://brownkit.readthedocs.io/en/latest/api/)

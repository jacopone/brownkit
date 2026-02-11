# BrownKit Examples

This directory contains practical examples of using BrownKit to transform brownfield codebases.

## Available Examples

### 1. Basic Python Transformation (`basic-python/`)

A simple Python project transformation demonstrating the complete brownfield workflow.

**What's Included:**
- `before/` - Messy Python project with poor structure, no tests, high complexity
- `after/` - Clean, tested, production-ready Python project
- Step-by-step walkthrough

**Learn:**
- Running brownfield assessment
- Fixing directory structure
- Adding test infrastructure
- Installing quality gates

**Time:** ~15 minutes

---

### 2. CI/CD Integration (`ci-integration/`)

Examples of integrating BrownKit with CI/CD pipelines.

**What's Included:**
- GitHub Actions workflows
- Pre-commit hook examples
- Status validation scripts

**Learn:**
- Automated brownfield checks in PR workflows
- Graduation status validation
- Coverage tracking integration

**Time:** ~10 minutes

---

## Running the Examples

### Prerequisites

```bash
# Install BrownKit
pip install brownkit

# Or install from source
cd /path/to/brownkit
pip install -e .[dev]
```

### Basic Python Example

```bash
# Navigate to example
cd examples/basic-python/before

# Run brownfield workflow
brownfield assess
brownfield structure
brownfield testing
brownfield quality
brownfield graduate

# Compare with after/
diff -r . ../after
```

### CI Integration Example

```bash
# Copy workflow to your project
cp examples/ci-integration/.github/workflows/brownfield-check.yml \
   /path/to/your/project/.github/workflows/

# Add status check to PR
# (See ci-integration/README.md for details)
```

---

## Contributing Examples

Have a great BrownKit transformation example? We'd love to include it!

**Guidelines:**
- Real-world or realistic projects
- Clear before/after comparison
- Documented steps (README.md)
- Under 1MB total size

See [CONTRIBUTING.md](../CONTRIBUTING.md) for submission process.

---

## Example Matrix

| Example | Language | Difficulty | Topics Covered |
|---------|----------|------------|----------------|
| basic-python | Python | Beginner | Full workflow, structure, testing, quality |
| ci-integration | Any | Intermediate | GitHub Actions, automation, validation |

---

## Additional Resources

- [Full Documentation](https://brownkit.readthedocs.io)
- [API Reference](https://brownkit.readthedocs.io/en/latest/api/)
- [GitHub Discussions](https://github.com/jacopone/brownkit/discussions)

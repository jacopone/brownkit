# CI/CD Integration Examples

Examples of integrating BrownKit with continuous integration pipelines.

## GitHub Actions Integration

### 1. Brownfield Status Check

Validate that your project maintains brownfield graduation status.

**File**: `.github/workflows/brownfield-check.yml`

```yaml
name: Brownfield Status Check

on:
  pull_request:
    branches: [ main ]

jobs:
  check-graduation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install BrownKit
        run: pip install brownkit

      - name: Check brownfield status
        run: |
          STATUS=$(brownfield status --json | jq -r '.current_phase')
          echo "Current phase: $STATUS"

          if [ "$STATUS" != "graduated" ]; then
            echo "❌ Project not graduated from brownfield workflow"
            echo "Current phase: $STATUS"
            brownfield status --verbose
            exit 1
          fi

          echo "✅ Project graduated - maintaining production standards"

      - name: Validate readiness gates
        run: |
          brownfield validate --json > validation.json
          cat validation.json | jq .

          PASSED=$(cat validation.json | jq -r '.gates_passed')
          TOTAL=$(cat validation.json | jq -r '.gates_total')

          if [ "$PASSED" != "$TOTAL" ]; then
            echo "❌ Some gates failing: $PASSED/$TOTAL passed"
            exit 1
          fi

          echo "✅ All $TOTAL gates passing"
```

**What This Does:**
- Runs on every pull request
- Checks if project is in "graduated" phase
- Validates all 7 readiness gates
- Fails PR if quality standards slip

---

### 2. Pre-commit Hook Integration

Ensure developers can't commit code that violates brownfield standards.

**File**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: brownfield-status
        name: Check Brownfield Status
        entry: bash -c 'brownfield status --json | jq -e ".current_phase == \"graduated\"" > /dev/null || (echo "❌ Project not graduated. Run: brownfield graduate" && exit 1)'
        language: system
        pass_filenames: false
        stages: [commit]

      - id: brownfield-validate
        name: Validate Readiness Gates
        entry: bash -c 'brownfield validate || (echo "❌ Gates failing. Fix issues before committing." && exit 1)'
        language: system
        pass_filenames: false
        stages: [push]
```

**Installation:**
```bash
pip install pre-commit
pre-commit install
```

**What This Does:**
- Checks graduation status on every commit
- Validates gates before every push
- Prevents degraded code from being committed

---

### 3. Automated Re-assessment

Periodically re-assess your project to detect quality drift.

**File**: `.github/workflows/brownfield-reassess.yml`

```yaml
name: Weekly Brownfield Re-assessment

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight
  workflow_dispatch:  # Manual trigger

jobs:
  reassess:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install BrownKit
        run: pip install brownkit

      - name: Run re-assessment
        run: |
          brownfield assess --force

      - name: Check for regression
        run: |
          CURRENT_PHASE=$(brownfield status --json | jq -r '.current_phase')

          if [ "$CURRENT_PHASE" != "graduated" ]; then
            echo "⚠️ Quality regression detected!"
            echo "Phase changed to: $CURRENT_PHASE"
            echo "Action required: Run brownfield workflow to restore quality"

            # Create issue
            gh issue create \
              --title "Quality Regression Detected - $CURRENT_PHASE phase" \
              --body "Automated re-assessment detected quality regression. Project phase: $CURRENT_PHASE. Please run brownfield workflow to restore quality standards." \
              --label "quality,brownfield"
          else
            echo "✅ No quality regression detected"
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload assessment report
        uses: actions/upload-artifact@v3
        with:
          name: assessment-report
          path: .specify/memory/assessment-report.md
```

**What This Does:**
- Runs weekly assessment automatically
- Detects quality regressions (coverage drop, complexity increase)
- Creates GitHub issue if regression detected
- Uploads assessment report as artifact

---

### 4. Coverage Tracking Integration

Track test coverage over time with Codecov.

**File**: `.github/workflows/coverage.yml`

```yaml
name: Coverage Tracking

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .[dev]
          pip install brownkit

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term

      - name: Check coverage threshold
        run: |
          COVERAGE=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')

          # Get brownfield target
          TARGET=$(brownfield status --json | jq -r '.coverage_target // 60')

          echo "Coverage: $COVERAGE%"
          echo "Target: $TARGET%"

          if (( $(echo "$COVERAGE < $TARGET" | bc -l) )); then
            echo "❌ Coverage below brownfield target: $COVERAGE% < $TARGET%"
            exit 1
          fi

          echo "✅ Coverage meets brownfield target"

      - name: Upload to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          fail_ci_if_error: false
        env:
          CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

---

## Quick Setup Guide

### 1. Copy Workflows to Your Project

```bash
# From your project root
mkdir -p .github/workflows

# Copy brownfield check
cp examples/ci-integration/.github/workflows/brownfield-check.yml \
   .github/workflows/

# Commit and push
git add .github/workflows/brownfield-check.yml
git commit -m "ci: add brownfield status check"
git push
```

### 2. Required Secrets

Add these secrets to your GitHub repository (Settings → Secrets):

- `CODECOV_TOKEN` - For coverage tracking (get from codecov.io)
- `GH_TOKEN` - Usually `${{ secrets.GITHUB_TOKEN }}` (automatically provided)

### 3. Enable Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Copy configuration
cp examples/ci-integration/.pre-commit-config.yaml .

# Install hooks
pre-commit install

# Test
pre-commit run --all-files
```

---

## Best Practices

### 1. Fail Fast on Regressions

Don't let quality slip. Use strict checks:

```yaml
- name: Strict validation
  run: |
    brownfield validate || exit 1
```

### 2. Track Metrics Over Time

Export metrics to JSON and track trends:

```bash
brownfield status --json > metrics.json
# Upload to metrics service
```

### 3. Automated Remediation PRs

Create PRs automatically when drift detected:

```yaml
- name: Create remediation PR
  if: failure()
  run: |
    brownfield testing --coverage-target 0.6
    git checkout -b fix/quality-regression
    git add .
    git commit -m "fix: restore brownfield quality standards"
    gh pr create --title "Fix Quality Regression" --body "Automated quality restoration"
```

### 4. Notify Team on Regression

Use GitHub notifications or Slack:

```yaml
- name: Notify on Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "⚠️ Brownfield quality regression detected in ${{ github.repository }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Integration Checklist

- [ ] Copied brownfield-check.yml workflow
- [ ] Enabled required branch protections
- [ ] Added Codecov token (if using coverage tracking)
- [ ] Installed pre-commit hooks
- [ ] Tested workflow with test PR
- [ ] Configured Slack/email notifications (optional)
- [ ] Set up weekly re-assessment (optional)

---

## Troubleshooting

**Issue**: `brownfield: command not found`
- **Fix**: Ensure BrownKit is installed in CI: `pip install brownkit`

**Issue**: Workflow fails with "state.json not found"
- **Fix**: Project not initialized. Run `brownfield assess` first

**Issue**: Gates fail unexpectedly
- **Fix**: Run `brownfield validate --verbose` locally to diagnose

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [BrownKit CLI Reference](https://brownkit.readthedocs.io)
- [Codecov Integration Guide](https://docs.codecov.com/docs/github-actions)

# BrownKit: Monitor

**Monitor post-graduation quality metrics and detect regressions.**

This command tracks your project's health after graduation by comparing current metrics against the baseline established at graduation. It detects quality regressions and triggers workflow re-entry when critical thresholds are breached.

## What This Command Does

1. **Current Assessment**: Runs lightweight assessment to get current metrics
2. **Baseline Comparison**: Compares against graduation baseline
3. **Regression Detection**: Identifies metrics that have degraded
4. **Severity Classification**: Categorizes regressions (INFO, WARNING, CRITICAL)
5. **Re-entry Trigger**: Recommends workflow re-entry for critical regressions

## When to Use

Run monitoring:
- **Periodically**: Weekly or bi-weekly health checks
- **After major changes**: Large refactoring, dependency updates
- **Pre-release**: Before deploying to production
- **CI integration**: Automated checks in pipeline
- **Post-deployment**: Verify production code quality

## Workflow Position

```
ASSESSMENT → PLANNING → REMEDIATION → VALIDATION → GRADUATION → [YOU ARE HERE]
                                                                  SPEC_KIT_READY
```

**Prerequisites**: Project must have graduated (SPEC_KIT_READY phase).

## Regression Severity Levels

### INFO (Informational)
- Minor metric fluctuations (< 70% of threshold)
- No action required
- Example: Coverage dropped 2% (threshold: 5%)

### WARNING (Approaching Threshold)
- Metric approaching threshold (70-99% of threshold)
- Review recommended
- Example: Coverage dropped 4% (threshold: 5%)

### CRITICAL (Threshold Breached)
- Metric exceeded threshold
- Immediate action required
- Triggers workflow re-entry recommendation
- Example: Coverage dropped 7% (threshold: 5%)

## Default Monitoring Thresholds

Based on constitution and graduation metrics:

**Test Coverage**:
- WARNING: Drop > 3.5% from baseline
- CRITICAL: Drop > 5% from baseline

**Complexity**:
- WARNING: Increase > 14% from baseline
- CRITICAL: Increase > 20% from baseline

**Security**:
- CRITICAL: Any new critical vulnerabilities (zero tolerance)
- WARNING: High vulnerabilities increased

**Build Status**:
- CRITICAL: Build failing (zero tolerance)
- WARNING: Build warnings increased

## Expected Output

```
📊 Post-Graduation Monitoring Report
====================================

Project: brownkit
Phase: SPEC_KIT_READY
Last Graduation: 2025-10-15
Monitoring Period: 11 days

Baseline Metrics (Graduation):
  Test Coverage: 85.0%
  Complexity Avg: 8.2
  Critical Vulns: 0
  Build Status: passing

Current Metrics:
  Test Coverage: 83.0% (↓ 2.0%)
  Complexity Avg: 9.1 (↑ 10.9%)
  Critical Vulns: 0 (→ 0)
  Build Status: passing (→)

Regression Analysis:
  ⚠️  WARNING: Test coverage dropped 2.0% (threshold: 5.0%)
     - Baseline: 85.0%, Current: 83.0%
     - Recommendation: Add tests for recently modified modules

  ℹ️  INFO: Complexity increased 10.9% (threshold: 20.0%)
     - Baseline: 8.2, Current: 9.1
     - Still within acceptable range

Overall Status: ✅ HEALTHY
  - No critical regressions detected
  - 1 warning requires attention
  - Continue using Spec-Kit workflow
```

## Monitoring Report (Critical Regression)

```
📊 Post-Graduation Monitoring Report
====================================

Current Metrics:
  Test Coverage: 78.0% (↓ 7.0%)
  Complexity Avg: 10.5 (↑ 28.0%)
  Critical Vulns: 2 (↑ 2)
  Build Status: failing

Regression Analysis:
  ❌ CRITICAL: Test coverage dropped 7.0% (threshold: 5.0%)
     - Baseline: 85.0%, Current: 78.0%
     - Re-entry recommended

  ❌ CRITICAL: Complexity increased 28.0% (threshold: 20.0%)
     - Baseline: 8.2, Current: 10.5
     - Re-entry recommended

  ❌ CRITICAL: 2 new critical vulnerabilities (zero tolerance)
     - CVE-2025-1234, CVE-2025-5678
     - Re-entry recommended

  ❌ CRITICAL: Build status changed to failing
     - Immediate fix required

Overall Status: ❌ CRITICAL REGRESSIONS DETECTED

RECOMMENDATION: Trigger BrownKit workflow re-entry
  1. Run /brownkit.assess to re-baseline
  2. Review regression root causes
  3. Create remediation plan for regressions
  4. Complete workflow to restore quality standards
```

## Workflow Re-entry

When critical regressions are detected:

1. **Assessment**: Run `/brownkit.assess` to get fresh baseline
2. **Planning**: Generate plan targeting regression fixes
3. **Remediation**: Execute fixes
4. **Validation**: Verify regressions resolved
5. **Re-graduation**: Update constitution if standards changed

## Custom Thresholds

Override default thresholds by updating constitution:

```yaml
regression_thresholds:
  test_coverage_drop: 10.0  # More lenient (default: 5.0)
  complexity_increase: 15.0  # Stricter (default: 20.0)
  critical_vulnerabilities: 0  # Zero tolerance (default)
  build_failures: 0  # Zero tolerance (default)
```

## Next Steps

### No Regressions:
- Continue using Spec-Kit workflow
- Monitor regularly (weekly/bi-weekly)
- Maintain quality standards from constitution

### Warnings Detected:
- Review warning details
- Address minor issues proactively
- Prevent escalation to critical

### Critical Regressions:
- **Immediate**: Run `/brownkit.assess`
- **Plan**: Create targeted remediation
- **Execute**: Fix critical issues
- **Verify**: Re-run monitoring

## Technical Details

- **Command**: `brownfield monitor` (CLI) or orchestrator
- **Input**: Graduation baseline from state
- **Output**: Monitoring report with regressions
- **Prerequisites**: SPEC_KIT_READY phase
- **Duration**: 2-3 minutes (lightweight assessment)

## CI/CD Integration

Integrate monitoring into CI pipeline:

```yaml
# .github/workflows/quality-monitoring.yml
name: Quality Monitoring
on: [push, pull_request]

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run BrownKit Monitoring
        run: brownfield monitor
      - name: Fail on critical regressions
        if: failure()
        run: echo "Critical regressions detected!"
```

## Error Handling

If monitoring fails:
- Ensure project has graduated (check with `brownfield status`)
- Verify baseline metrics exist in state
- Re-run graduation if baseline is missing
- Check that assessment tools are available

---

**Note**: Monitoring is non-destructive and can be run as often as needed. It provides early warning of quality degradation before issues become severe.

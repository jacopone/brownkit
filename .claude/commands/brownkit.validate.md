# BrownKit: Validate

**Verify remediation improvements and check graduation readiness.**

This command validates that remediation tasks achieved their goals by re-running all assessments and comparing metrics against baseline. It determines if the project meets graduation criteria for Spec-Kit readiness.

## What This Command Does

1. **Enforces Workflow**: Validates remediation is complete before validation
2. **Re-assessment**: Runs full assessment to get current metrics
3. **Comparison**: Compares current metrics against baseline from initial assessment
4. **Gate Checking**: Verifies all 7 readiness gates are satisfied
5. **Report Generation**: Creates detailed validation report

## Workflow Position

```
ASSESSMENT → PLANNING → REMEDIATION → [YOU ARE HERE] → GRADUATION → SPEC-KIT READY
                                       VALIDATION
```

**Prerequisites**: Remediation must be completed successfully.

## Validation Checks

### 1. Metric Improvements
- **Test Coverage**: Must meet or exceed target (typically 80%+)
- **Complexity**: Average CCN reduced below threshold (< 10)
- **Vulnerabilities**: Critical and high severity issues resolved
- **Build Status**: Build must pass without errors

### 2. Readiness Gates (7 Gates)

1. **Structure Gate**: Organized directory structure, no dead code
2. **Testing Gate**: Coverage ≥ target, all test types present
3. **Quality Gate**: Complexity under control, no critical linting issues
4. **Security Gate**: No critical vulnerabilities, secrets removed
5. **Build Gate**: Build system configured and passing
6. **CI Gate**: CI/CD pipeline set up and green
7. **Documentation Gate**: README, docs coverage above threshold

### 3. Regression Prevention
- No metric worse than baseline
- Build still passing
- No new critical issues introduced

## Expected Output

After validation, you'll see:
- **✅ Passed Gates**: Which readiness gates are satisfied
- **❌ Failed Gates**: Which gates still need work
- **Metric Comparison**: Before/after metrics side-by-side
- **Improvement Summary**: Percentage improvements per category
- **Next Steps**: Graduate or return to remediation

## Validation Report Structure

```
Validation Report
=================

Readiness Gates:
  ✅ Structure Gate (100% - organized, no dead code)
  ✅ Testing Gate (85% coverage, all types present)
  ⚠️  Quality Gate (complexity: 9.8 avg, target: < 10)
  ✅ Security Gate (0 critical, 1 high remaining)
  ✅ Build Gate (passing)
  ❌ CI Gate (pipeline not configured)
  ✅ Documentation Gate (78% coverage)

Overall: 5/7 gates passed (71%)

Metric Improvements:
  Test Coverage: 45% → 85% (+40%)
  Complexity Avg: 18.3 → 9.8 (-46%)
  Critical Vulns: 3 → 0 (-100%)
  Build Status: failing → passing

Remaining Issues:
  - CI pipeline needs GitHub Actions workflow
  - 1 high-severity vulnerability in dependencies
```

## Conditional Outcomes

### All Gates Pass → Graduation Eligible
- Run `/brownkit.graduate` to generate constitution and complete workflow

### Some Gates Fail → Return to Remediation
- Review failed gates
- Update remediation plan for remaining issues
- Re-run `/brownkit.remediate` (resumes from checkpoint)
- Validate again after fixes

### Regressions Detected → Critical Review
- Identify which remediation tasks caused regressions
- Revert problematic changes
- Update plan to avoid regression
- Re-run remediation and validation

## Next Steps

### If Validation Passes:
1. Review the validation report and celebrate improvements
2. Run `/brownkit.graduate` to generate constitution
3. Transition to Spec-Kit workflow

### If Validation Fails:
1. Review failed gates and remaining issues
2. Update remediation plan or create new tasks
3. Re-run `/brownkit.remediate` to address issues
4. Run `/brownkit.validate` again

## Technical Details

- **Command**: `brownfield validate` (CLI) or orchestrator
- **Input**: Current codebase + baseline metrics from state
- **Output**: Validation report + gate status in state
- **Prerequisites**: Completed remediation phase
- **Duration**: 2-5 minutes (same as assessment)

## Error Handling

If validation fails:
- Review the detailed validation report
- Check that remediation tasks completed successfully
- Ensure build system is properly configured
- Re-run assessment manually if metrics seem incorrect

## Validation vs Assessment

- **Assessment**: Initial baseline metrics (entry point)
- **Validation**: Comparison against baseline to verify improvements
- **Both use same tools**: Structure, testing, quality analysis
- **Validation adds**: Gate checking, regression detection, readiness scoring

---

**Note**: Validation can be re-run multiple times. Each run updates metrics and re-checks gates. Use this to verify fixes after returning to remediation.

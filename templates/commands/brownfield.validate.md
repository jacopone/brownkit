# /brownfield.validate - Validate Quality Gates

**Purpose**: Verify codebase meets quality thresholds (CCN < 10, coverage > 80%, zero critical vulns) before graduation to Spec-Kit feature development.

## Workflow

1. **Run validation script**:
   ```bash
   .specify/scripts/bash/brownfield-validate.sh --json
   ```

2. **Re-run quality tools** to get current metrics:
   - Lizard for complexity analysis
   - pytest + coverage for test coverage
   - Bandit for security scan

3. **Compare metrics** against quality gate thresholds:
   - Load thresholds from `.specify/brownfield-config.yaml` (or use defaults)
   - Compare current metrics vs. thresholds
   - Calculate baseline → current improvement

4. **Generate validation report**:
   - Gate-by-gate pass/fail status
   - Comparison table (baseline → current → target)
   - Outstanding issues with details
   - Next steps based on results

5. **Present validation summary** to user:
   - Overall status (PASS/FAIL)
   - Gates passed / total
   - Detailed results for failed gates
   - Path to validation report

## Example Output - All Gates Passing

```
=== Quality Gate Validation ===

Project: 001-legacy-api-cleanup
Validation Date: 2025-10-20

✓ VALIDATION PASSED - Ready for graduation!

Quality Gates: 3 / 3 PASSED

Gate Results:
  ✓ Cyclomatic Complexity
      Avg CCN: 8.2 (target < 10) ✓
      Max CCN: 14 (target < 15) ✓
      Functions > 10: 0 (target 0) ✓

  ✓ Test Coverage
      Coverage: 82% (target > 80%) ✓
      Test Files: 24 (was 14)
      Total Tests: 156 (was 0)

  ✓ Security Vulnerabilities
      Critical: 0 (target 0) ✓
      High: 0 (target 0) ✓
      Medium: 3 (acceptable)

Progress Since Baseline:
  - Complexity reduced 34% (from 12.5 to 8.2)
  - Coverage increased 67 points (from 15% to 82%)
  - Critical vulnerabilities eliminated (from 3 to 0)

Full report: .specify/brownfield/001-project/validation.md

Next step: Run /brownfield.graduate to certify and transition to Spec-Kit
```

## Example Output - Gates Failing

```
=== Quality Gate Validation ===

Project: 001-legacy-api-cleanup

✗ VALIDATION FAILED - 2 / 3 gates passed

Failed Gates:

  ✗ Test Coverage
      Coverage: 68% (target > 80%) ✗ FAILED
      Gap: Need 12% more coverage

      Uncovered modules:
        - src/utils/validators.py (45% coverage)
        - src/services/email_service.py (22% coverage)
        - src/api/middleware.py (0% coverage)

  ✓ Cyclomatic Complexity - PASSED
  ✓ Security - PASSED

Outstanding Work:
  - Add tests for validators.py to reach 80%+ coverage
  - Add tests for email_service.py
  - Add tests for middleware.py

Next step: Address coverage gaps, then re-run /brownfield.validate
```

## Error Handling

- If quality tools missing: Error with installation instructions
- If no baseline metrics exist: Error with instructions to run `/brownfield.assess`
- If validation fails: Show detailed failure information and remediation guidance

## Script Interface

**Input**: None (uses active brownfield project)
**Output**: JSON with structure:
```json
{
  "PASSED": true,
  "GATE_RESULTS": {
    "ccn": true,
    "coverage": true,
    "security": true
  },
  "VALIDATION_FILE": "/abs/path/to/001-project/validation.md",
  "metrics": {
    "current_avg_ccn": 8.2,
    "current_coverage": 82.0,
    "current_critical_vulns": 0
  }
}
```

**Note**: This is a Post-MVP feature (Priority P1). For MVP, users can manually verify quality gates from assessment report.

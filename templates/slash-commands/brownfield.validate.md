# Brownfield Validate

Check all 7 readiness gates to determine graduation eligibility.

```bash
brownfield validate
```

Validates these gates:
1. **Test Coverage** ≥60% on core business logic
2. **Cyclomatic Complexity** <10 (or documented in complexity-justification.md)
3. **Directory Structure** - Follows ecosystem conventions
4. **Build Status** - Clean build with <10 warnings
5. **API Documentation** ≥80% of public APIs documented
6. **Security** - 0 critical vulnerabilities
7. **Git Hygiene** - No secrets or large binaries

If all gates pass:
- State advances to GRADUATION phase
- Project is ready for `brownfield graduate`

If gates fail:
- Shows failed gates with remediation guidance
- Recommends which phase to return to
- Provides specific steps to address issues

Options:
- `--gate NAME` - Validate specific gate only
- `--fail-fast` - Stop at first gate failure
- `--report PATH` - Save validation report to file

Example output:
```
✅ Validating readiness gates...

Gate 1: Test Coverage
  Threshold: ≥60%
  Current: 65%
  Status: ✅ PASS

Gate 2: Cyclomatic Complexity
  Threshold: <10 (or documented)
  Current: Max 15 (3 exceptions documented)
  Status: ✅ PASS

...

═══════════════════════════════════
Result: ALL GATES PASSED ✅
═══════════════════════════════════

Next step: brownfield graduate
```

After all gates pass:
```bash
brownfield graduate
```

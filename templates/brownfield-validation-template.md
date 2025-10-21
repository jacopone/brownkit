# Brownfield Validation Report

**Project**: {{PROJECT_NAME}}
**Validation Date**: {{DATE}}
**Brownfield Directory**: {{BROWNFIELD_DIR}}

## Validation Summary

**Overall Status**: {{OVERALL_STATUS}}

Quality gates passed: **{{GATES_PASSED}}** / **{{GATES_TOTAL}}**

{{PASS_FAIL_ICON}} Ready for graduation to Spec-Kit feature development

---

## Quality Gate Results

### Gate 1: Cyclomatic Complexity

**Status**: {{CCN_STATUS}}

| Metric | Baseline | Current | Target | Result |
|--------|----------|---------|--------|--------|
| Average CCN | {{BASELINE_AVG_CCN}} | {{CURRENT_AVG_CCN}} | < 10 | {{CCN_AVG_RESULT}} |
| Max CCN | {{BASELINE_MAX_CCN}} | {{CURRENT_MAX_CCN}} | < 15 | {{CCN_MAX_RESULT}} |
| Functions > 10 | {{BASELINE_FUNCTIONS_OVER}} | {{CURRENT_FUNCTIONS_OVER}} | 0 | {{CCN_FUNCTIONS_RESULT}} |

{{CCN_DETAILS}}

---

### Gate 2: Test Coverage

**Status**: {{COVERAGE_STATUS}}

| Metric | Baseline | Current | Target | Result |
|--------|----------|---------|--------|--------|
| Coverage % | {{BASELINE_COVERAGE}}% | {{CURRENT_COVERAGE}}% | > 80% | {{COVERAGE_RESULT}} |
| Test Files | {{BASELINE_TEST_FILES}} | {{CURRENT_TEST_FILES}} | N/A | {{TEST_FILES_RESULT}} |
| Total Tests | {{BASELINE_TOTAL_TESTS}} | {{CURRENT_TOTAL_TESTS}} | N/A | {{TOTAL_TESTS_RESULT}} |

{{COVERAGE_DETAILS}}

---

### Gate 3: Security Vulnerabilities

**Status**: {{SECURITY_STATUS}}

| Severity | Baseline | Current | Target | Result |
|----------|----------|---------|--------|--------|
| Critical | {{BASELINE_CRITICAL}} | {{CURRENT_CRITICAL}} | 0 | {{CRITICAL_RESULT}} |
| High | {{BASELINE_HIGH}} | {{CURRENT_HIGH}} | 0 | {{HIGH_RESULT}} |
| Medium | {{BASELINE_MEDIUM}} | {{CURRENT_MEDIUM}} | N/A | {{MEDIUM_RESULT}} |
| Low | {{BASELINE_LOW}} | {{CURRENT_LOW}} | N/A | {{LOW_RESULT}} |

{{SECURITY_DETAILS}}

---

## Progress Analysis

### Improvements Since Baseline

**Complexity**:
- Average CCN reduced by {{CCN_IMPROVEMENT}}% (from {{BASELINE_AVG_CCN}} to {{CURRENT_AVG_CCN}})
- {{COMPLEXITY_IMPROVEMENT_SUMMARY}}

**Test Coverage**:
- Coverage increased by {{COVERAGE_IMPROVEMENT}} percentage points (from {{BASELINE_COVERAGE}}% to {{CURRENT_COVERAGE}}%)
- {{COVERAGE_IMPROVEMENT_SUMMARY}}

**Security**:
- Critical vulnerabilities reduced from {{BASELINE_CRITICAL}} to {{CURRENT_CRITICAL}}
- {{SECURITY_IMPROVEMENT_SUMMARY}}

---

## Outstanding Issues

{{OUTSTANDING_ISSUES}}

---

## Next Steps

{{NEXT_STEPS}}

---

## Validation Details

**Quality Tools Used**:
- Complexity Analysis: {{COMPLEXITY_TOOL}} ({{COMPLEXITY_VERSION}})
- Coverage Analysis: {{COVERAGE_TOOL}} ({{COVERAGE_VERSION}})
- Security Scan: {{SECURITY_TOOL}} ({{SECURITY_VERSION}})

**Validation Command**:
```bash
/brownfield.validate
```

**Full Tool Outputs**:
- Complexity: [/tmp/brownfield-complexity.json](/tmp/brownfield-complexity.json)
- Coverage: [/tmp/brownfield-coverage.json](/tmp/brownfield-coverage.json)
- Security: [/tmp/brownfield-security.json](/tmp/brownfield-security.json)

---

*This validation report was generated automatically by Brownfield-Kit.*

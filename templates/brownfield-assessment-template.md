# Brownfield Assessment Report

**Project**: {{PROJECT_NAME}}
**Assessment Date**: {{DATE}}
**Brownfield Directory**: {{BROWNFIELD_DIR}}

## Executive Summary

This assessment analyzed **{{TOTAL_FILES}}** files containing **{{TOTAL_LINES}}** lines of code. The codebase exhibits the following quality metrics:

- **Complexity**: Average CCN of {{AVG_CCN}}, maximum CCN of {{MAX_CCN}}
- **Test Coverage**: {{COVERAGE_PERCENT}}% coverage
- **Security**: {{CRITICAL_VULNS}} critical vulnerabilities, {{HIGH_VULNS}} high-severity issues

## Code Complexity Analysis

### Overall Metrics
- **Average Cyclomatic Complexity**: {{AVG_CCN}}
- **Maximum Cyclomatic Complexity**: {{MAX_CCN}}
- **Functions Over Threshold (CCN > 10)**: {{FUNCTIONS_OVER_THRESHOLD}}
- **Files Analyzed**: {{FILES_ANALYZED}}

### Complexity Hotspots

{{COMPLEXITY_HOTSPOTS}}

## Test Coverage Analysis

### Coverage Metrics
- **Coverage Percentage**: {{COVERAGE_PERCENT}}%
- **Test Files**: {{TEST_FILES}}
- **Total Tests**: {{TOTAL_TESTS}}
- **Test Framework**: {{TEST_FRAMEWORK}}

### Uncovered Areas

{{COVERAGE_GAPS}}

## Security Vulnerability Scan

### Vulnerability Summary
- **Critical Severity**: {{CRITICAL_VULNS}}
- **High Severity**: {{HIGH_VULNS}}
- **Medium Severity**: {{MEDIUM_VULNS}}
- **Low Severity**: {{LOW_VULNS}}
- **Total Issues**: {{TOTAL_ISSUES}}

### Critical Vulnerabilities

{{CRITICAL_VULN_DETAILS}}

### High Severity Issues

{{HIGH_VULN_DETAILS}}

## Recommendations

### Immediate Actions (Critical Priority)
1. Address {{CRITICAL_VULNS}} critical security vulnerabilities
2. Refactor {{HIGH_COMPLEXITY_COUNT}} functions with CCN > 15
3. Add test coverage for {{UNTESTED_MODULES}} untested modules

### Medium Priority
1. Reduce average complexity from {{AVG_CCN}} to below 10
2. Increase test coverage from {{COVERAGE_PERCENT}}% to 80%+
3. Address {{HIGH_VULNS}} high-severity security issues

### Long-term Improvements
1. Establish pre-commit hooks for quality gates
2. Implement continuous monitoring of complexity metrics
3. Document architectural patterns in constitution

## Next Steps

1. Review this assessment report
2. Run `/brownfield.plan` to generate actionable remediation plan
3. Prioritize tasks based on severity and impact
4. Begin remediation with highest-priority items

---

**Note**: This assessment provides a baseline snapshot. Run `/brownfield.assess` again after remediation to measure improvement.

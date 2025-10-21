# Brownfield Remediation Plan

**Project**: {{PROJECT_NAME}}
**Plan Created**: {{DATE}}
**Assessment Reference**: [assessment.md](assessment.md)

## Plan Summary

This plan addresses **{{TOTAL_ISSUES}}** identified issues across three categories:
- **{{COMPLEXITY_ISSUE_COUNT}}** complexity hotspots
- **{{COVERAGE_ISSUE_COUNT}}** test coverage gaps
- **{{SECURITY_ISSUE_COUNT}}** security vulnerabilities

**Estimated Effort**: {{ESTIMATED_HOURS}} hours
**Recommended Timeline**: {{TIMELINE_WEEKS}} weeks

## Quality Gate Targets

- [ ] **Cyclomatic Complexity**: Reduce average from {{CURRENT_AVG_CCN}} to < 10
- [ ] **Test Coverage**: Increase from {{CURRENT_COVERAGE}}% to > 80%
- [ ] **Security**: Resolve all {{CRITICAL_VULNS}} critical vulnerabilities
- [ ] **Build**: All tests passing, no regressions

## Phase 1: Critical Security Fixes

**Priority**: IMMEDIATE
**Estimated Time**: {{SECURITY_HOURS}} hours

{{SECURITY_TASKS}}

**Checkpoint**: All critical vulnerabilities resolved, security scan shows zero high/critical issues

---

## Phase 2: Complexity Reduction

**Priority**: HIGH
**Estimated Time**: {{COMPLEXITY_HOURS}} hours

{{COMPLEXITY_TASKS}}

**Checkpoint**: Average CCN < 10, no functions with CCN > 15

---

## Phase 3: Test Coverage Improvement

**Priority**: MEDIUM
**Estimated Time**: {{TESTING_HOURS}} hours

{{TESTING_TASKS}}

**Checkpoint**: Test coverage > 80%, all critical paths covered

---

## Phase 4: Validation & Documentation

**Priority**: FINAL
**Estimated Time**: {{VALIDATION_HOURS}} hours

### Tasks
1. **Run final validation**: Execute `/brownfield.validate` to verify all quality gates
2. **Document patterns**: Update constitution with validated architectural decisions
3. **Review checklist**: Ensure 100% completion of quality-gates.md
4. **Graduate**: Run `/brownfield.graduate` to certify codebase as AI-ready

**Checkpoint**: All quality gates pass, ready for `/speckit.specify`

---

## Task Execution Guidelines

### Automated Execution
To execute this plan automatically:
```bash
/brownfield.remediate
```

This will:
- Execute tasks sequentially
- Run tests after each change (checkpoint validation)
- Stop if any checkpoint fails
- Log progress to execution-log.md

### Manual Execution
To execute manually:
1. Work through tasks in order listed
2. After each task, run tests to verify no regressions
3. Check off completed items in quality-gates.md checklist
4. Run `/brownfield.validate` after each phase

### Checkpoint Failures
If a checkpoint fails:
1. Review execution-log.md for error details
2. Fix the issue manually
3. Re-run tests to verify fix
4. Resume remediation from failed checkpoint

---

## Risk Assessment

### High Risk Changes
{{HIGH_RISK_CHANGES}}

### Mitigation Strategies
1. **Git commits after each task**: Enable rollback if needed
2. **Test-driven refactoring**: Write tests before refactoring complex functions
3. **Incremental changes**: Break large refactorings into smaller steps
4. **Code review**: Have team member review high-risk changes

---

## Success Criteria

This plan is complete when:
- [X] All critical security vulnerabilities resolved
- [X] Average cyclomatic complexity < 10
- [X] Test coverage > 80%
- [X] All tests passing
- [X] `/brownfield.validate` reports all gates passed
- [X] Quality gates checklist 100% complete

---

**Next Step**: Review this plan, then run `/brownfield.remediate` to begin execution or proceed manually task-by-task.

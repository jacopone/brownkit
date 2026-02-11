# Brownfield Assess

Run brownfield assessment to analyze codebase structure, metrics, and tech debt.

```bash
brownfield assess
```

This command will:
1. Detect primary language and framework
2. Collect baseline metrics (LOC, complexity, test coverage)
3. Identify tech debt categories
4. Generate assessment report
5. Initialize brownfield state

Options:
- `--mode [quick|thorough]` - Analysis depth (default: quick)
- `--output PATH` - Custom report location (default: brownfield-assessment-report.md)

After completion, proceed to structure remediation:
```bash
brownfield structure
```

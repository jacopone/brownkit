# /brownfield.assess - Assess Technical Debt Hotspots

**Purpose**: Identify complexity hotspots, test coverage gaps, and security vulnerabilities with concrete metrics to prioritize remediation efforts.

## Workflow

1. **Run assessment script**:
   ```bash
   .specify/scripts/bash/brownfield-assess.sh --json
   ```

2. **Parse JSON output** to get:
   - `ASSESSMENT_FILE`: Path to assessment.md
   - `BROWNFIELD_DIR`: Path to numbered project directory
   - `METRICS`: Complexity, coverage, and security metrics

3. **Present assessment summary** to user:
   - Quality metrics overview
   - Top complexity hotspots
   - Coverage gaps
   - Critical security issues
   - Path to detailed assessment report

4. **Suggest next step**: Run `/brownfield.plan` to generate remediation plan

## Example Output

```
=== Technical Debt Assessment Complete ===

Project: 001-legacy-api-cleanup
Assessment Date: 2025-10-20

Quality Metrics:
  Complexity: Avg CCN 12.5, Max CCN 45 (12 functions > 10)
  Coverage: 15% (85% gap)
  Security: 3 critical, 8 high-severity vulnerabilities

Top Complexity Hotspots:
  1. src/services/user_service.py:process_user() - CCN 45
  2. src/api/routes.py:handle_request() - CCN 38
  3. src/utils/validators.py:validate_input() - CCN 22

Critical Security Issues:
  1. SQL Injection risk in src/database/queries.py:142
  2. Hardcoded credentials in src/config.py:23
  3. Unsafe deserialization in src/api/parser.py:67

Full report: .specify/brownfield/001-legacy-api-cleanup/assessment.md

Next step: Run /brownfield.plan to generate remediation plan
```

## Error Handling

- If quality tools missing: Warn and skip that analysis (e.g., "lizard not found, skipping complexity analysis")
- If no tests exist: Report 0% coverage and flag as critical gap
- If analysis fails: Display error with tool output for debugging

## Script Interface

**Input**: None (analyzes current directory)
**Output**: JSON with structure:
```json
{
  "ASSESSMENT_FILE": "/abs/path/to/001-project/assessment.md",
  "BROWNFIELD_DIR": "/abs/path/to/.specify/brownfield/001-project",
  "METRICS": {
    "avg_ccn": 12.5,
    "max_ccn": 45,
    "coverage": 15.0,
    "critical_vulns": 3,
    "high_vulns": 8
  }
}
```

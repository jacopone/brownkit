# Brownfield Status

Show current workflow state and progress.

```bash
brownfield status
```

Displays:
- Current workflow phase
- Graduation status
- Baseline vs current metrics comparison
- Phase completion timeline (with --verbose)
- Re-entry events (if any)
- Next recommended step

**Example output:**
```
📊 Brownfield Workflow Status

Current Phase: 🧪 TESTING
Graduation: ⏳ In Progress

Metrics Overview:

┌───────────────────────────┬──────────┬──────────┬─────────┐
│ Metric                    │ Baseline │ Current  │ Change  │
├───────────────────────────┼──────────┼──────────┼─────────┤
│ Test Coverage             │ 0.0%     │ 45.0%    │ +45.0%  │
│ Avg Complexity            │ 8.5      │ 7.2      │ -1.3    │
│ Critical Vulnerabilities  │ 2        │ 0        │ -2      │
│ Lines of Code             │ 12,450   │ 12,450   │ -       │
└───────────────────────────┴──────────┴──────────┴─────────┘

Next Steps:
  Run: brownfield quality
```

**JSON output:**
```bash
brownfield status --json
```

Returns structured JSON with:
- schema_version
- current_phase
- graduated (boolean)
- graduation_timestamp
- baseline_metrics
- current_metrics
- phase_timestamps
- re_entry_events

Useful for CI/CD integration and scripting.

**Verbose mode:**
```bash
brownfield status --verbose
```

Additionally shows:
- Complete phase timeline with timestamps
- All metric changes over time
- Detailed re-entry event information

**Re-entry events display:**
```
⚠ Re-entry Events:

1. coverage_drop - ⚠ ACTIVE
   Detected: 2025-10-21 15:30:12
   Baseline: 0.65 → Current: 0.48
   Threshold: 0.50
   Re-entry Phase: testing

2. complexity_increase - ✅ RESOLVED
   Detected: 2025-10-20 10:15:00
   Baseline: 8.5 → Current: 12.3
   Threshold: 12.0
   Re-entry Phase: quality
   Resolved: 2025-10-20 14:22:00
```

Options:
- `--json` - Output as JSON
- `--verbose`, `-v` - Show detailed metrics and timeline

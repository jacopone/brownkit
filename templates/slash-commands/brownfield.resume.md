# Brownfield Resume

Resume interrupted phase from checkpoint.

```bash
brownfield resume
```

When a brownfield phase is interrupted (Ctrl+C, system crash, connection loss), this command allows resuming from the last checkpoint instead of starting over.

**How it works:**
1. Lists all available checkpoints with status
2. Identifies interrupted phases
3. Shows completed vs pending tasks
4. Displays next task to resume from
5. Provides command to continue

**Example output:**
```
🔄 Resume Interrupted Workflow

Available Checkpoints:

┌──────────────┬──────────────┬───────────┬─────────┬─────────────────────┐
│ Phase        │ Status       │ Completed │ Pending │ Timestamp           │
├──────────────┼──────────────┼───────────┼─────────┼─────────────────────┤
│ testing      │ ⚠ Interrupted│ 15        │ 8       │ 2025-10-21 14:32:10 │
│ structure    │ ✓ Complete   │ 12        │ 0       │ 2025-10-21 13:15:42 │
└──────────────┴──────────────┴───────────┴─────────┴─────────────────────┘

Resuming Phase: testing
  Completed tasks: 15
  Pending tasks: 8

Next Task:
  Generate contract tests for UserService API

✓ Ready to resume testing phase

Run: brownfield testing to continue from checkpoint
```

Options:
- `--restart` - Clear checkpoint and restart phase from beginning

Restart example:
```bash
brownfield resume --restart
```

Output:
```
--restart flag set: Clearing checkpoint and restarting phase

✓ Checkpoint cleared for testing phase

Run: brownfield testing to restart from beginning
```

**Checkpoint locations:**
- Saved to: `.brownfield/checkpoints/<phase>-checkpoint.json`
- Includes: completed tasks, pending tasks, timestamp, context data
- Automatically created during long-running operations

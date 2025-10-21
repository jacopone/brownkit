# /brownfield.ingest - Analyze Codebase Architecture

**Purpose**: Analyze existing codebase to discover frameworks, architectural patterns, and conventions that should be preserved during remediation.

## Workflow

1. **Run codebase analysis script**:
   ```bash
   .specify/scripts/bash/brownfield-ingest.sh --json
   ```

2. **Parse JSON output** to get:
   - `ANALYSIS_FILE`: Path to generated codebase-analysis.md
   - Discovered frameworks (Flask, FastAPI, Django, etc.)
   - Architectural patterns (Repository, Service Layer, MVC)
   - Code statistics (files, lines, languages)

3. **Update constitution** with discovered patterns in `.specify/memory/constitution.md`

4. **Present analysis summary** to user:
   - Framework detected
   - Primary architectural patterns
   - Codebase statistics
   - Path to detailed analysis document

## Example Output

```
=== Codebase Analysis Complete ===

Framework Detected: FastAPI 0.104.0
Architecture Pattern: Service Layer + Repository Pattern
Primary Language: Python (9,823 LOC)

Codebase Statistics:
- Total Files: 156
- Source Files: 142
- Test Files: 14
- Documentation: 12

Analysis saved to: .specify/memory/codebase-analysis.md

Constitution updated with discovered patterns.

Next step: Run /brownfield.assess to identify technical debt hotspots
```

## Error Handling

- If not in a Spec-Kit project: Error with installation instructions
- If analysis fails: Display error and suggest manual review
- If no clear framework detected: Report as "Framework: Unknown" and proceed

## Script Interface

**Input**: None (analyzes current directory)
**Output**: JSON with structure:
```json
{
  "ANALYSIS_FILE": "/abs/path/to/codebase-analysis.md",
  "framework": "FastAPI",
  "architecture": "Service Layer",
  "stats": {
    "total_files": 156,
    "total_lines": 12450,
    "languages": {"python": 9823}
  }
}
```

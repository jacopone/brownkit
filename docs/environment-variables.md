---
status: active
created: 2025-10-21
updated: 2025-10-21
type: reference
lifecycle: persistent
---

# Environment Variables

Brownfield-Kit supports environment variables for customizing behavior without command-line flags.

## Configuration Variables

### BROWNFIELD_PROJECT_ROOT

Override the project root directory.

**Default**: Current working directory (`pwd`)

**Example**:
```bash
export BROWNFIELD_PROJECT_ROOT=/path/to/project
brownfield assess
```

**Use case**: Running brownfield commands from outside the project directory.

---

### BROWNFIELD_STATE_DIR

Override the state directory where workflow state is stored.

**Default**: `$PROJECT_ROOT/.specify/memory`

**Example**:
```bash
export BROWNFIELD_STATE_DIR=/custom/state/dir
brownfield status
```

**Use case**: Centralizing state files for multi-project workflows.

---

### BROWNFIELD_REPORTS_DIR

Override the reports directory where assessment and graduation reports are saved.

**Default**: `$PROJECT_ROOT/.specify/memory`

**Example**:
```bash
export BROWNFIELD_REPORTS_DIR=/custom/reports/dir
brownfield assess --output /custom/reports/dir/assessment.md
```

**Use case**: Storing reports in a dedicated documentation directory.

---

### BROWNFIELD_TEMPLATES_DIR

Specify a custom templates directory for graduation artifacts.

**Default**: Built-in templates (from package installation)

**Example**:
```bash
export BROWNFIELD_TEMPLATES_DIR=/custom/templates
brownfield graduate
```

**Use case**: Customizing spec/plan/tasks templates for organization-specific workflows.

---

### BROWNFIELD_DEBUG

Enable debug logging to console.

**Values**: `true`, `1`, `yes` (case-insensitive)

**Default**: `false`

**Example**:
```bash
export BROWNFIELD_DEBUG=true
brownfield assess
```

**Output**:
```
🔍 Assessing codebase...

Debug: Project root: /home/user/myproject
Debug: State dir: /home/user/myproject/.specify/memory
```

**Use case**: Troubleshooting path resolution issues.

---

### BROWNFIELD_ANALYSIS_MODE

Set default analysis mode for `brownfield assess`.

**Values**: `quick` | `full`

**Default**: `quick`

**Example**:
```bash
export BROWNFIELD_ANALYSIS_MODE=full
brownfield assess  # Uses full analysis without --full flag
```

**Use case**: CI/CD pipelines that always want comprehensive analysis.

---

### BROWNFIELD_FORCE_LANGUAGE

Force language detection override for all commands.

**Values**: `python` | `javascript` | `rust` | `go`

**Default**: Auto-detection

**Example**:
```bash
export BROWNFIELD_FORCE_LANGUAGE=python
brownfield assess  # Skips language detection
```

**Use case**: Multi-language projects where you want to process one language at a time.

---

## Precedence Rules

Environment variables are overridden by command-line flags:

```bash
export BROWNFIELD_ANALYSIS_MODE=full
brownfield assess --quick  # --quick takes precedence, uses quick mode
```

```bash
export BROWNFIELD_FORCE_LANGUAGE=python
brownfield assess --language rust  # Processes as Rust, not Python
```

---

## CI/CD Integration Example

```yaml
# .github/workflows/brownfield.yml
name: Brownfield Quality Check

on:
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    env:
      BROWNFIELD_ANALYSIS_MODE: full
      BROWNFIELD_DEBUG: true
      BROWNFIELD_REPORTS_DIR: /tmp/brownfield-reports

    steps:
      - uses: actions/checkout@v3

      - name: Install brownfield
        run: pip install brownfield-kit

      - name: Assess codebase
        run: brownfield assess

      - name: Validate gates
        run: brownfield validate --json > validation.json

      - name: Check status
        run: |
          STATUS=$(brownfield status --json | jq -r '.current_phase')
          echo "Current phase: $STATUS"

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: brownfield-reports
          path: /tmp/brownfield-reports/
```

---

## Docker Integration Example

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install brownfield
RUN pip install brownfield-kit

# Set brownfield configuration
ENV BROWNFIELD_PROJECT_ROOT=/app
ENV BROWNFIELD_STATE_DIR=/app/.brownfield/state
ENV BROWNFIELD_REPORTS_DIR=/app/.brownfield/reports
ENV BROWNFIELD_ANALYSIS_MODE=full

COPY . /app

# Run assessment
RUN brownfield assess

CMD ["brownfield", "status", "--json"]
```

---

## Development Workflow Example

```bash
# Developer's .envrc (using direnv)
export BROWNFIELD_DEBUG=true
export BROWNFIELD_ANALYSIS_MODE=quick
export BROWNFIELD_TEMPLATES_DIR=$HOME/.brownfield/templates

# Now all brownfield commands use these settings
brownfield assess
brownfield structure
brownfield testing
```

---

## Troubleshooting

### "State file not found" error

Check state directory configuration:

```bash
export BROWNFIELD_DEBUG=true
brownfield status
# Shows: Debug: State dir: /path/to/state
```

Verify the directory exists:

```bash
ls -la $(printenv BROWNFIELD_STATE_DIR || echo ".specify/memory")
```

### Custom templates not loading

Verify templates directory structure:

```bash
tree $BROWNFIELD_TEMPLATES_DIR
# Should contain:
# ├── spec-template.md
# ├── plan-template.md
# └── tasks-template.md
```

### Project root detection issues

Force project root explicitly:

```bash
export BROWNFIELD_PROJECT_ROOT=/absolute/path/to/project
cd /anywhere
brownfield status  # Still uses /absolute/path/to/project
```
